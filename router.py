import os
import shutil
import json
import yaml
from datetime import datetime
from flask import Flask
from flask import session
from flask import render_template
from flask import redirect
from flask import request
from flask import send_file
from flask import url_for
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from flask_login import current_user
from flask_login import login_user
from flask_login import logout_user
from flask_login import login_required

from app.utility import forms
from app.utility.login import LoginHandler
from app.tools.visualiser.dashboards.full.dash import ViewDashboard 
from app.tools.visualiser.dashboards.explore.dash import ExploreDashboard 
from app.storage.storage_strategies.neo4j.storage import Neo4jStorage
from app.tools.db_interface.db_interface import DatabaseInterface
from app.tools.data_transformer.data_transformer import DataTransformer
from app.tools.utility.graph_analyser import analyse
from app.tools.utility.markdown_generator import generate_markdown
from app.tools.utility.markdown_generator import get_filename

root_dir = "app"
static_dir = os.path.join(root_dir, "assets")
template_dir = os.path.join(root_dir, "templates")
sessions_dir = os.path.join(root_dir, "sessions")
graph_store = os.path.join(sessions_dir,"graph_backup")

if not os.path.isdir(sessions_dir):
    os.mkdir(sessions_dir)
if not os.path.isdir(graph_store):
    os.mkdir(graph_store)

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

server = Flask(__name__, static_folder=static_dir, template_folder=template_dir)
server.debug = True

db_host = os.environ.get("NEO4J_HOST", "localhost")
db_auth = os.environ.get("NEO4J_AUTH", "neo4j/Radeon12300")
db_user, db_pass = db_auth.split("/")
login_graph_name = "login_manager"

db_interface = DatabaseInterface()
data_transformer = DataTransformer()
# Constrict to n4j for now.
storage_graph = Neo4jStorage(**config["STORAGE"])

# Tools
view_dash = ViewDashboard(storage_graph,__name__, server)
view_dash.app.enable_dev_tools(debug=True)

explore_dash = ExploreDashboard(storage_graph,__name__, server)
explore_dash.app.enable_dev_tools(debug=True)

app = DispatcherMiddleware(
    server,
    {
        view_dash.pathname: view_dash.app.server,
        explore_dash.pathname: explore_dash.app.server,
    },
)

server.config["SESSION_PERMANENT"] = True
server.config["SESSION_TYPE"] = "filesystem"
server.config["SESSION_FILE_THRESHOLD"] = 100
server.config["SECRET_KEY"] = "Secret"
server.config["SESSION_FILE_DIR"] = os.path.join(root_dir, "flask_sessions")
login_manager = LoginHandler(server, sessions_dir)
login_manager.login_view = "login"
fn_size_threshold = os.environ.get("FILESIZE_THRESHOLD", 106384)


@login_manager.user_loader
def load_user(user_name):
    if login_manager.admin is not None and user_name == login_manager.admin.username:
        return login_manager.admin
    for user in login_manager.get_users():
        if user.username == user_name:
            return user
    return None


@server.route("/login", methods=["GET", "POST"])
def login():
    create_user_form = forms.CreateUserForm()
    create_admin_form = forms.CreateAdminForm()
    if not current_user.is_authenticated:
        if login_manager.admin is None:
            if create_admin_form.validate_on_submit():
                admin = login_manager.add_admin(
                    create_admin_form.username.data, create_admin_form.password.data
                )
                login_user(admin)
                return redirect(url_for("index"))
            else:
                return render_template(
                    "signup.html", create_admin_form=create_admin_form
                )
        if create_user_form.validate_on_submit():
            un = create_user_form.username.data
            pw = create_user_form.password.data
            user = login_manager.get_user(un, pw)
            if user is None:
                if login_manager.does_exist(un):
                    return render_template(
                        "signup.html",
                        create_user_form=create_user_form,
                        invalid_username=True,
                    )
                user = login_manager.add_user(un, pw)
            login_user(user)
            next = request.args.get("next")
            return redirect(next or url_for("index"))
        else:
            return render_template("signup.html", create_user_form=create_user_form)
    next = request.args.get("next")
    return redirect(next or url_for("index"))


@server.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("index")


@server.route("/", methods=["GET", "POST"])
@server.route("/index", methods=["GET", "POST"])
@login_required
def index():
    return render_template("index.html", is_admin=current_user.is_admin)


@server.route("/graph-admin", methods=["GET", "POST"])
@login_required
def graph_admin():
    if not _is_admin():
        return render_template("invalid_route.html", invalid_credentials=True)
    
    save_restore_graph = forms.save_restore_graph(graph_store)
    if save_restore_graph.reset.id in request.form.keys():
        graphs = prepare_graphs(refresh=True)
        for graph in graphs:
            storage_graph.add_rdf_graph(graph)
    elif save_restore_graph.rebuild.id in request.form.keys():
        graphs = prepare_graphs(refresh=False)
        for graph in graphs:
            storage_graph.add_rdf_graph(graph)
    elif save_restore_graph.save.id in request.form.keys():
        filename = save_restore_graph.filename.data
        if filename == "" or filename is None:
            now = datetime.now()
            filename = now.strftime("%Y%m%d-%H%M")
        filename = os.path.join(graph_store,filename+".json")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(storage_graph.export())
    elif save_restore_graph.restore.id in request.form.keys():
        fn = os.path.join(graph_store, request.form["files"])
        storage_graph.load(fn)

    return render_template("admin.html", is_admin=current_user.is_admin,
                           save_restore_graph=save_restore_graph)


@server.route("/graph_metrics", methods=["GET", "POST"])
@login_required
def graph_metrics():
    data = analyse(storage_graph)
    generate_markdown(data)
    return render_template("graph_metrics.html",
                           is_admin=current_user.is_admin,
                           metric_data=data)


@server.route("/visualiser", methods=["GET", "POST"])
@login_required
def visualiser():
    return redirect(view_dash.pathname)
    
@server.route("/explore", methods=["GET", "POST"])
@login_required
def explore():
    node_id = request.form.get("node_id")
    if node_id is not None:
        session["node_id"] = node_id
    return redirect(explore_dash.pathname)

@server.route("/download_report", methods=["POST"])
def download_report():    
    filename = get_filename()
    return send_file(filename, as_attachment=True)

@server.before_request
def before_request_func():
    if current_user.get_id() is None:
        return
    user_dir = os.path.join(sessions_dir, current_user.get_id())
    try:
        os.makedirs(user_dir)
    except FileExistsError:
        pass
    session["user_dir"] = user_dir


def _is_admin():
    admin = login_manager.admin
    if (
        admin.username == current_user.get_id()
        and admin.password == current_user.password
    ):
        return True
    return False


def prepare_graphs(refresh: bool):
    pe, ce = db_interface.download_all(refresh=refresh)
    replacement_map = {}
    pe = data_transformer.replace_identifiers(pe, replacement_map)
    ce = data_transformer.replace_identifiers(ce, replacement_map)
    pe = data_transformer.replace_references(pe, replacement_map)
    ce = data_transformer.replace_references(ce, replacement_map)
    return data_transformer.transform_data(pe + ce)