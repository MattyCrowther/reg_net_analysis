import random
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix, ConfusionMatrixDisplay
import matplotlib.pyplot as plt
from app.model.model import model

def build_edge_df(edge_df, label, embeddings):
    return pd.DataFrame([
        {
            "src_id": row["src"],
            "dst_id": row["dst"],
            "src_emb": embeddings.get(row["src"]),
            "dst_emb": embeddings.get(row["dst"]),
            "label": label
        }
        for _, row in edge_df.iterrows()
        if row["src"] in embeddings and row["dst"] in embeddings
    ])

def sample_negative(edge_list, size):
    existing = {(n.identifier, v.identifier) for n, v, _ in edge_list}
    all_nodes = list({n.identifier for n, v, _ in edge_list} |
                     {v.identifier for n, v, _ in edge_list})
    neg = set()
    while len(neg) < size:
        s = random.choice(all_nodes)
        d = random.choice(all_nodes)
        if s != d and (s, d) not in existing and (d, s) not in existing:
            neg.add((s, d))
    return list(neg)

def get_id_map(handler):
    return handler.get_id_map()

def generate_embeddings(handler, graph_name):
    embeddings_df = handler.procedure.node_2_vec(graph_name)
    return dict(zip(embeddings_df["nodeId"], embeddings_df["embedding"]))

def build_edge_frame_from_edges(edges, id_map):
    return pd.DataFrame([
        {"src": id_map[n.identifier], "dst": id_map[v.identifier]}
        for n, v, _ in edges
        if n.identifier in id_map and v.identifier in id_map
    ])

def build_sampled_negatives(edges, id_map):
    return pd.DataFrame([
        {"src": id_map[s], "dst": id_map[d]}
        for s, d in sample_negative(edges, len(edges))
        if s in id_map and d in id_map
    ])

def build_feature_df(pos_df, neg_df, embeddings):
    pos = build_edge_df(pos_df, 1, embeddings)
    neg = build_edge_df(neg_df, 0, embeddings)
    df = pd.concat([pos, neg], ignore_index=True)
    df = df.dropna(subset=["src_emb", "dst_emb"])
    df["features"] = df.apply(lambda row: row["src_emb"] + row["dst_emb"], axis=1)
    return df

def run_link_prediction(handler, gn="interaction"):
    nv_interaction = model.identifiers.objects.interaction
    try:
        handler.project.drop(gn)
    except ValueError:
        pass

    int_types = model.get_all_subclasses(nv_interaction)
    edges = handler.get_edges(node_type=int_types)
    random.shuffle(edges)
    split = int(len(edges) * 0.8)
    training_edges = edges[:split]
    testing_edges = edges[split:]

    training_ids = list({n.identifier for n, v, _ in training_edges} |
                        {v.identifier for n, v, _ in training_edges})
    edge_labels = list({e.type for _, _, e in training_edges})
    proj_res = handler.project.sub_graph(gn, node_ids=training_ids, edge_labels=edge_labels)

    embeddings = generate_embeddings(handler, proj_res.name())
    id_map = get_id_map(handler)

    pos_train = build_edge_frame_from_edges(training_edges, id_map)
    neg_train = build_sampled_negatives(training_edges, id_map)

    def compute_distances(edge_df, embeddings):
        dists = []
        for _, row in edge_df.iterrows():
            src, dst = row["src"], row["dst"]
            if src in embeddings and dst in embeddings:
                v1 = np.array(embeddings[src])
                v2 = np.array(embeddings[dst])
                dists.append(np.linalg.norm(v1 - v2))
        return dists

    pos_dists = compute_distances(pos_train, embeddings)
    neg_dists = compute_distances(neg_train, embeddings)

    plt.hist(pos_dists, bins=50, alpha=0.5, label="Positive")
    plt.hist(neg_dists, bins=50, alpha=0.5, label="Negative")
    plt.xlabel("Embedding distance")
    plt.ylabel("Frequency")
    plt.title("Embedding distance distribution")
    plt.legend()
    plt.tight_layout()
    plt.savefig("embedding_distance_hist.png", dpi=300, bbox_inches="tight")

    train_df = build_feature_df(pos_train, neg_train, embeddings)
    X_train = np.array(train_df["features"].tolist())
    y_train = train_df["label"].astype(int).values

    clf = LogisticRegression(max_iter=1000,verbose=1)
    clf.fit(X_train, y_train)

    pos_test = build_edge_frame_from_edges(testing_edges, id_map)
    neg_test = build_sampled_negatives(testing_edges, id_map)
    test_df = build_feature_df(pos_test, neg_test, embeddings)

    X_test = np.array(test_df["features"].tolist())
    y_test = test_df["label"].astype(int).values

    y_pred = clf.predict(X_test)
    y_prob = clf.predict_proba(X_test)[:, 1]

    print("\n=== TEST SET EVALUATION ===")
    print("AUC:", roc_auc_score(y_test, y_prob))
    print("Classification report:\n", classification_report(y_test, y_pred))

    cm = confusion_matrix(y_test, y_pred)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm)
    disp.plot(cmap="Blues")
    plt.title("Confusion Matrix")
    plt.tight_layout()
    plt.savefig("confusion_matrix.png")

    plt.figure(figsize=(10, 4))
    plt.bar(range(len(clf.coef_[0])), np.abs(clf.coef_[0]))
    plt.xlabel("Feature Index")
    plt.ylabel("Weight Magnitude")
    plt.title("Trained Weights Magnitude (Logistic Regression)")
    plt.tight_layout()
    plt.savefig("weight_magnitudes.png")