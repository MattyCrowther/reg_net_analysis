import re

start_val = (0,90,75)
hue_step = 20
sat_mod = 0.8
light_mod = 0.8
max_hue = 340
min_sat = 20
min_light = 18

class ColorPicker:
    def __init__(self,shuffle=True):
        self._colors = self._build_color(shuffle)

    def __iter__(self):
        for col in self._flatten():
            yield str(col)

    def __getitem__(self,index):
        try:
            return str(self._flatten()[index])
        except IndexError:
            return str(self._flatten()[-1])

    def increase_shade(self,hsl_val):
        hsl = HSLVal.parse(hsl_val)
        s = int(hsl.s * sat_mod)
        l = int(hsl.l * light_mod)
        if s < min_sat and l < min_light:
            s = start_val[1]
            l = start_val[2]
        hsl.s = s
        hsl.l = l
        return str(hsl)
    
    def get_color(self,hue, saturation, lightness):
        return str(HSLVal(hue,saturation,lightness))
    
    def _build_color(self,shuffle=True):
        cur_hue = start_val[0]
        hsl_list = []
        while cur_hue <= max_hue:
            cur_sat = start_val[1]
            cur_light = start_val[2]
            color_list = []
            while cur_sat > min_sat and cur_light > min_light:
                hsl_val = HSLVal(cur_hue,cur_sat,cur_light)
                color_list.append(hsl_val)
                cur_sat = int(cur_sat * sat_mod)
                cur_light = int(cur_light * light_mod)
            cur_hue += hue_step
            hsl_list.append(color_list)

        if shuffle:
            hsl_list = self._determinable_shuffle(hsl_list)
        return hsl_list

    def _determinable_shuffle(self,hsl_list):
        '''
        Only shuffle whole columns or whole rows.
        '''
        num_cols = len(hsl_list)
        # Swap each pair of rows index (0,1 - 2,3 - 4,5 ...)
        num_rows = len(max(hsl_list,key=len))
        next_row_i = 1
        while next_row_i < num_rows:
            hsl_list = self._swap_columns(hsl_list,next_row_i-1,next_row_i)
            next_row_i +=2

        # Move Columns based on odd|even and away from centre.
        # Ensures not only most distinct neigbours but also index 0 and 1 are 
        # most distinct as they are most used colors.
        mid_val = int(num_cols/2)
        # From middle column, 
        new_hsl_list = [hsl_list[mid_val]]
        # Add each odd column left
        new_hsl_list += hsl_list[1:mid_val:2]
        # Add each even column right.
        new_hsl_list += hsl_list[mid_val+2::2]
        # Add each odd column right.
        new_hsl_list += hsl_list[mid_val+1::2]
        # Add each even column left.
        new_hsl_list += hsl_list[0:mid_val:2]

        return new_hsl_list

    def _swap_columns(self,hsl_list, pos1, pos2):
        for item in hsl_list:
            item[pos1], item[pos2] = item[pos2], item[pos1]
        return hsl_list
        
    def _flatten(self):
        '''
        Flatterns row by row.
        '''
        flat_list = []
        for col in range(0,len(max(self._colors,key=len))): 
            for row in range(0,len(self._colors)):
                flat_list.append(self._colors[row][col])
        return flat_list

class HSLVal:
    def __init__(self,h,s,l):
        self.h = int(h)
        self.s = int(s)
        self.l = int(l)

    @classmethod
    def parse(cls,hsl):
        m=re.match("^\s*(\w+)\s*\((.*)\)",hsl)
        values = m.group(2).replace("%","")
        return cls(*values.split(","))

    def __repr__(self):
        return f'hsl({self.h},{self.s}%,{self.l}%)'

