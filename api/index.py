from distutils.log import debug
from fileinput import filename
from flask import *
import os
from werkzeug.utils import secure_filename
from csv import DictReader
 
#UPLOAD_FOLDER = os.path.join('staticFiles', 'uploads')
UPLOAD_FOLDER = '/tmp'
 
# Define allowed files
ALLOWED_EXTENSIONS = {'csv'}
 
app = Flask(__name__)
global html_data
global all_weapon_set
 
# Configure upload file path flask
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
 
app.secret_key = 'This is your secret key. Obviosuly not the real one'
 
 
@app.route('/', methods=['GET', 'POST'])
def uploadFile():
    if request.method == 'POST':
      # upload file flask
        f = request.files.get('file')
 
        # Extracting uploaded file name
        data_filename = secure_filename(f.filename)
 
        f.save(os.path.join(app.config['UPLOAD_FOLDER'],
                            data_filename))
 
        session['uploaded_data_file_path'] = os.path.join(app.config['UPLOAD_FOLDER'],
                     data_filename)
        
        #########################
        
        global html_data
        html_data = ""

        def create_html_text(some_text, separator):
            res_text =str(some_text) + separator
            return res_text
        
        # reading the values from a csv file
        # file should be format as follows:
        # player,str,int,will,fort,vit, - headers that will not be used
        # player1,100,0,100,0,0         - weapon stats and the players who owns the weapon

        with open(os.path.join(app.config['UPLOAD_FOLDER'], data_filename),'r', encoding='utf-8-sig') as file:
            
            dict_reader = DictReader(file)
            
            header = []
            player_data={}
            index = {}
            
            for row in dict_reader:
                value_lst = []
                sub_d={}
                
                try:
                    value_lst.append(int(row['str']))
                except:
                    html_data += "Your file contains missing data. Please write 0 for missing STR attributes."
                    return render_template('index2.html',data_var=html_data)
                
                try:
                    value_lst.append(int(row['int']))
                except:
                    html_data += "Your file contains missing data. Please write 0 for missing INT attributes."
                    return render_template('index2.html',data_var=html_data)
                
                try:
                    value_lst.append(int(row['will']))
                except:
                    html_data += "Your file contains missing data. Please write 0 for missing WILL attributes."
                    return render_template('index2.html',data_var=html_data)
                
                try:
                    value_lst.append(int(row['fort']))
                except:
                    html_data += "Your file contains missing data. Please write 0 for missing FORT attributes."
                    return render_template('index2.html',data_var=html_data)
                                
                try:
                    value_lst.append(int(row['vit']))
                except:
                    html_data += "Your file contains missing data. Please write 0 for missing VIT attributes."
                    return render_template('index2.html',data_var=html_data)
                
                
                # no key names - automatically generates       
                if row['player'] not in header:
                    index[row['player']]=1
                    key = 'w'+str(index[row['player']])+str(row['player'])
                    index[row['player']]+=1
                    
                    sub_d[key]=tuple(value_lst)
                    player_data[row['player']]=sub_d
                    
                    header.append(row['player'])
                else:
                    key = 'w'+str(index[row['player']])+str(row['player'])
                    index[row['player']]+=1
                    
                    sub_d[key]=tuple(value_lst)
                    player_data[row['player']].update(sub_d)
                    
        file.close()
        try:
           os.remove(os.path.join(app.config['UPLOAD_FOLDER'], data_filename))
           html_data += 'File succesfully deleted. No data is stored on the server.<br><br>'
        except Exception as e:
           html_data += "We encounter some problem with deleting your file. Vercel will soon delete your data.<br><br>"
           app.logger.warning(e)
           

        # we need players name as a list in order to iterate using an index in a recursive function
        players = list(player_data.keys())

        #function _check_if_worse can check if a weapon from a player is worse than everything else and can be scraped instead of holding in inventory
        def check_if_worse(player,weapon):
            weapons = player_data[player]
            stat1_lower = 0
            stat2_lower = 0
            stat3_lower = 0
            stat1_eq = 0
            stat2_eq = 0
            stat3_eq = 0
            
            for w in weapons.values():
                if (w == weapon):
                    continue
                stat1_lower = 1
                stat2_lower = 1
                stat3_lower = 1
                
                stat1_eq = 0
                stat2_eq = 0
                stat3_eq = 0
                
                index = 0
                for i in range(0,len(weapon)):
                    if weapon[i] != 0:
                        index +=1
                        if index == 1:
                            if weapon[i]>=w[i]:
                                stat1_lower = 0
                            if weapon[i]==w[i]:
                                stat1_eq = 1
                        elif index == 2:
                            if weapon[i]>=w[i]:
                                stat2_lower = 0
                            if weapon[i]==w[i]:
                                stat2_eq = 1
                        elif index == 3:
                            if weapon[i]>=w[i]:
                                stat2_lower = 0
                            if weapon[i]==w[i]:
                                stat2_eq = 1
                            
                        
                        
                if (stat1_lower and stat2_lower and stat3_lower):
                    return True
                if (stat1_eq and stat2_lower and stat3_lower):
                    return True
                if (stat2_eq and stat1_lower and stat3_lower):
                    return True
                if (stat3_eq and stat1_lower and stat2_lower):
                    return True
                if (stat1_eq and stat2_eq and stat3_lower):
                    return True
                if (stat2_eq and stat3_eq and stat1_lower):
                    return True
                if (stat1_eq and stat3_eq and stat3_lower):
                    return True
                
            return False
                        
        weapon_set=[]
        all_weapon_set =[]

        # function to generate all possible combinations of weapons in the ancestral tableau
        def GenerateSets(player_data, players, index):
            
            if (len(weapon_set)==4):
                
                weapon_set_with_total = list(weapon_set)
                
                weapon_set_with_total.append(
                    tuple(
                    ['total', 
                     tuple([weapon_set[0][1][i]+weapon_set[1][1][i]+weapon_set[2][1][i] + weapon_set[3][1][i] 
                            for i in range(0,len(weapon_set[0][1]))])]
                            )
                            )
                all_weapon_set.append(tuple(weapon_set_with_total))

                return 
            
            for w_values in player_data[players[index]].values():
                weapon_set.append(tuple([players[index],w_values]))
                GenerateSets(player_data, players, index+1)
                weapon_set.pop() 


        #parse the data and clean it
        to_remove = []
        for player, weapons in player_data.items():  
            for w_key, w in weapons.items():
                if check_if_worse(player,w):
                    to_remove.append([player,w_key])

        #create a new dict for cleaned data. This will be used in further calcualtions
        cleaned_player_data = dict(player_data)

        #print("The following weapons can be SALVAGED:")
        html_data += create_html_text("The following weapons can be SALVAGED:",'<br>')
        if to_remove:
            for item in to_remove:
                #print(item[1], cleaned_player_data[item[0]][item[1]],' can be salvaged.')
                html_data += create_html_text(str(item[1]) + ' ' + str(cleaned_player_data[item[0]][item[1]]) + ' can be salvaged.','<br>')
                del cleaned_player_data[item[0]][item[1]]
        else:
            #print("NONE. You have an optimal inventory of Ancestral Weapons.")
            html_data += create_html_text("NONE. You have an optimal inventory of Ancestral Weapons.",'<br>')

        # generate the sets in all_weapon_set
        for i in range(0,8):
            for j in range(i+1,8):
                for l in range(j+1,8):
                    for m in range(l+1,8):
                        new_dict={}
                        new_players=[players[i],players[j],players[l],players[m]]
                        new_dict[players[i]] = cleaned_player_data[players[i]]
                        new_dict[players[j]] = cleaned_player_data[players[j]]
                        new_dict[players[l]] = cleaned_player_data[players[l]]
                        new_dict[players[m]] = cleaned_player_data[players[m]]
                        GenerateSets(new_dict, new_players, 0)

        all_weapon_set=list(set(all_weapon_set))
        #this is sorting by the minimum of the total columns and in reverse,there are still duplicates
        all_weapon_set.sort(key = lambda x: min(x[4][1]), reverse=True)


        #display one set with the final values
        def display_best(our_set):
            global html_data
            for items in our_set[:-1]:
                #print (items[0],items[1])                    
                html_data += create_html_text(str(items[0])+' '+str(items[1]),'<br>')
            #list_attributes divided by 4 (integer result) represents the value of maximum bonus in game
            #print("\nFinal values in tableau:\n STR  INT  WILL FORT VIT")
            html_data += create_html_text("<br>Final values in tableau:<br> STR  INT  WILL FORT VIT",'<br>')
            #print(tuple(x//4 for x in our_set[-1][1]))
            html_data += create_html_text(str(tuple(x//4 for x in our_set[-1][1])),'<br>')

        #The nth (10) best sets
        #print('\nBEST 10 Sets of Ancestral Weapon are:\n')
        html_data += create_html_text("<br>BEST 10 Sets of Ancestral Weapon are:<br>",'<br>')
        
        for i in range(0,10):
            #print('\n----------#'+str(i+1)+'#----------')
            html_data += create_html_text('<br>----------#'+str(i+1)+'#----------','<br>')
            display_best(all_weapon_set[i])

        
        return render_template('index2.html',data_var=html_data)
    return render_template("index.html")
 
if __name__ == '__main__':
    print('Go time')
    app.run(debug=True)
