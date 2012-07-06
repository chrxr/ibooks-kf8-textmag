#!/usr/bin/python3

import os, shutil, zipfile, errno, re, io, codecs, sys
from bs4 import BeautifulSoup

def main():
    begin_path = 'files/'
    end_path = 'files/copy/'
    extract_path = 'files/extracted/'
    repub_path = 'files/repubbed/'
    blank_file = 'files/blank.xhtml'
    merged_loc = 'files/merged/'
    zip_list = [] 
    new_file_locs = {}
    div_list = []
    file_list = get_file_list(begin_path)
    print('Got file list\n')
    for infile in file_list:
        file_locs = {} 
        copy_file(infile, begin_path, end_path)
        print('Copied EPUB\n')
        infile = ext_changer(end_path, infile)
        print('Changed to Zip\n')
        zip_check(end_path, zip_list, infile)
        print('Checked we only have Zips\n')
        extract_list = zip_opener(end_path, infile, extract_path, file_locs)
        print('Opened Zip\n')
        #INSERT PROCESSING STUFF HERE
        #
        processing(extract_list, file_locs, new_file_locs, blank_file, merged_loc, div_list)
        print('Finished processing\n')
        #
        #
        re_zip(repub_path, extract_path, extract_list, new_file_locs)
        print('All done\n')

    
#LISTS INPUT FILES
    
def get_file_list(begin_path):
    file_list = []
    listing = os.listdir(begin_path)
    for infile in listing:
        this_file = infile
        current_ext = os.path.splitext(this_file)[1]
        if current_ext == '.epub':
            file_list.append(infile)
    return file_list

#BACKUPS UP INPUT FILES, WORKS ON COPIES

def copy_file(infile, begin_path, end_path):
        src = begin_path + infile
        dst = end_path
        shutil.copy2(src, dst)

        # Will have to revisit this as it overwrites files. Need to add exception

#CHANGES EPUB EXTENSIONS TO ZIP, AND VICE VERSA
def ext_changer(end_path, infile):
    base = os.path.splitext(infile)[0]
    current_ext = os.path.splitext(infile)[1]
    if current_ext == '.epub':
        file_path = end_path + infile
        new_file = end_path + base + '.zip'
        os.rename(file_path, new_file)
    elif current_ext == '.zip':
        file_path = end_path + infile
        new_file = end_path + base + '.epub'
        os.rename(file_path, new_file)
    return new_file

#CHECKS FOR ZIP FILES AND SAVES THEM TO LIST

def zip_check(end_path, zip_list, infile):
        current_ext = os.path.splitext(infile)[1]
        if current_ext == '.zip':
            zip_list.append(infile)
            
#OPENS ZIP FILES, CREATES DIR, CREATES DICT OF FILE LOCATIONS, AND EXTRACTS FILES TO FOLDER

def zip_opener(end_path, infile, extract_path, file_locs):
        extract_list = {}
        zipper = zipfile.ZipFile(infile, 'r')
        file_name = os.path.split(infile)[1]
        minus_ext = os.path.splitext(file_name)[0]
        file_locs[minus_ext] = zipper.namelist()
        new_path = extract_path + minus_ext
        mkdir_p(new_path)
        zipper.extractall(path = new_path)
        extract_list[minus_ext] = new_path
        return extract_list
          
## REZIPS FILE AND CONVERTS TO EPUB

def re_zip(repub_path, extract_path, extract_list, new_file_locs):
    searcher = re.compile('mimetype')
    for key in extract_list:
        extracted_path = extract_path + key + '/'
        zip_path = repub_path + key + '.zip'
        zipper = zipfile.ZipFile(zip_path, 'a')
        for index, value in new_file_locs.items():
            if key == index:
                for ind_file_name in value:
                    if re.search(searcher, ind_file_name):
                        zipper.write(extracted_path + ind_file_name, ind_file_name)
                        for ind_file_name in value:
                            if re.search(searcher, ind_file_name):
                                continue
                            else:    
                                zipper.write(extracted_path + ind_file_name, ind_file_name)
                    else:
                        continue
            else:
                continue
        zipper.close()
    listing = os.listdir(repub_path)
    for infile in listing:
        base = os.path.splitext(infile)[0]
        current_ext = os.path.splitext(infile)[1]
        if current_ext == '.zip':
            file_path = repub_path + infile
            new_file = repub_path + base + '.epub'
            os.rename(file_path, new_file)
        else:
            continue
        
#ALL THE MAIN STUFF HAPPENS HERE       
        
def processing(extract_list, file_locs, new_file_locs, blank_file, merged_loc, div_list):
    opf_finder = re.compile('\.opf')
    smil_finder = re.compile('\.smil')
    ncx_finder = re.compile('\.ncx')
    x_content_finder = re.compile('\.xhtml')
    h_content_finder = re.compile('\.html')
    style_finder = re.compile('\.css')
    vp_finder = re.compile('name="viewport"')
    head_finder = re.compile('\</metadata\>')
    px_width_finder = re.compile('width=[0-9]*px[^A-Za-z0-9]{1}')
    px_height_finder = re.compile('height=[0-9]*px[^A-Za-z0-9]{1}')
    width_finder = re.compile('width=[0-9]*[^A-Za-z0-9]{1}')
    height_finder = re.compile('height=[0-9]*[^A-Za-z0-9]{1}')
    smil_list = []
    content_list = []
    spine_order = []
    smil_folder = ''
    
#############  OBTAINING INFORMATION (THIS CAN PROBABLY BE SIMPLIFIED) #################### 
    
    #finding locations of key files & assigning to variables / lists
    for key in extract_list:
        for index, value in file_locs.items():
            if key == index:
                ind_ext_path = extract_list[key] + '/'
                for ind_file_name in value:
                    if re.search(opf_finder, ind_file_name):
                        opf_loc = ind_file_name
                        opf_name = os.path.split(opf_loc)[1]
                        content_dir = os.path.dirname(opf_loc)
                    if re.search(smil_finder, ind_file_name):
                        smil_list.append(ind_file_name)
                        smil_folder = os.path.split(smil_list[0])[0]
                    if re.search(ncx_finder, ind_file_name):
                        ncx_loc = ind_file_name
                    if re.search(x_content_finder, ind_file_name):
                        content_loc = os.path.split(ind_file_name)[0]
                        content_ext = os.path.splitext(ind_file_name)[1]
                        content_list.append(ind_file_name)
                    if re.search(h_content_finder, ind_file_name):
                        try:
                            if re.search(x_content_finder, content_list[0]):
                                print('ERROR: You have a mixture of html and xhtml docs. You can only use one or the other.')
                                sys.exit()
                        except:
                            content_loc = os.path.split(ind_file_name)[0]
                            content_ext = os.path.splitext(ind_file_name)[1]
                            content_list.append(ind_file_name)
                    if re.search(style_finder, ind_file_name):
                        style_loc = os.path.split(ind_file_name)[0]
            content_root = os.path.basename(content_loc) 
             
            #Loads files into BeautifulSoup
            opf_soup = load_file(ind_ext_path + opf_loc)
            
                        
            #Obtains viewport info
            a_content_file = io.open(ind_ext_path + content_list[-1], mode='r', encoding = 'UTF-8')
            text = a_content_file.readlines()
            a_content_file.close()
            for line in text:
                if re.search(vp_finder, line):
                    height_f = height_finder.search(line)
                    width_f = width_finder.search(line)
                    height_b = height_f.group(0)
                    width_b = width_f.group(0)
                    width = re.search('[^a-z=].*[^A-Za-z,"\']', width_b)
                    height = re.search('[^a-z=].*[^A-Za-z,"\']', height_b)
                    real_width = str(int(width.group())*2)
                    real_height = str(height.group())

                    
#############  END OF OBTAINING INFORMATION #################### 
                
#############  OPF FILE STUFF!!! #################### 
           
            #Obtains spine order
            
            result = opf_soup.findAll(attrs={'idref': True})
            for i in range(len(result)):
                output = result[i]['idref']
                spine_order.append(output)
                
            #Creates dictionary of files in order to merge them later
            c_dict = contents_dic(spine_order, opf_soup)
            
            #Obtains cover name
            cover_item = opf_soup.find(attrs={'name':'cover'})
            cover_name = cover_item['content']
            
            #Obtains title
            result = opf_soup.find('dc:title')
            title = result.find(text=True)
            
            #As mentioned above, files merged into spreads, returns c_dict with appended new file names (as last index for each spread, either 2 or 6)
            file_merger(blank_file, c_dict, title, ind_ext_path,  merged_loc, content_dir, content_ext, div_list)
            
            #Deleting old file and moving new files into content location
            mover_shaker(c_dict, merged_loc, ind_ext_path, content_dir, content_root)
            
            new_opf_soup = opf_content_editor(c_dict, opf_soup, content_loc, cover_name, title, content_root)
            
            css_inserter(real_height, real_width, ind_ext_path, style_loc, div_list)
           
            #Copies OPF file

            text = str(new_opf_soup.prettify())
            file = open(opf_name, "w")          
            split_file = text.split('\n')

            
            #Creates list of items to insert into <head> +  height and width and inserts them
            orig_res = '<meta name="original-resolution" content="' + real_width + 'x' + real_height + '"/>'
            head_insertion = ['<meta name="fixed-layout" content="true"/>', orig_res, '<meta name="book-type" content="children"/>']
            for line in split_file:
                if re.search(head_finder, line):
                    head_index = split_file.index(line)
            for el in head_insertion:
                split_file.insert(head_index, el)
                

    
            #Rewrites opf file with line breaks 
            for line in split_file:
                line_break = line + '\n'
                file.write(line_break)
            file.close()
            overwrite_files(opf_name, ind_ext_path + opf_loc)
            
#############  END OF OPF FILE STUFF!!! ####################              
            
#############  REMOVING FILES AND STUFF!!! #################### 
            
            #Remove smil files and folder
            if smil_folder is not '':
                smil_rmv_path = ind_ext_path + smil_folder
                regex = re.compile('')
                remove_directory(smil_rmv_path, regex)
                os.rmdir(smil_rmv_path)

            
            #Removes display-options file
            display_name = 'META-INF/com.apple.ibooks.display-options.xml'
            apple_path = ind_ext_path + display_name
            os.remove(apple_path)
            
#############  END OF REMOVING FILES AND STUFF!!! #################### 
            
            
#############  REPACKAGING FILE_LIST FOR RE_ZIP FUNCTION  #################### 

            root = ind_ext_path
            new_file_list = []
            for path, subdirs, files in os.walk(root):
                for name in files:
                    item = os.path.join(path, name)
                    l = list(item)
                    for i in range(len(l)):
                        result = re.sub(r'\\', '/', l[i])
                        l[i] = result
                    lstr = ''.join(l)
                    d = "/"
                    split_item =  [e+d for e in lstr.split(d) if e != ""]
                    split_item[-1] = re.sub('/', '', split_item[-1])
                    split_item[0:3] = []
                    conc_item = ''.join(split_item)
                    new_file_list.append(conc_item)

            list_builder = []
            for index, value in file_locs.items():
                for item in value:
                    list_builder.append(item)
            for item in smil_list:
                list_builder.remove(item)
            list_builder.remove(display_name)
            if smil_folder is not '':
                paths_to_remove = []
                paths_to_remove.append(smil_folder + '/')
                for paths in paths_to_remove:
                    try:
                        list_builder.remove(paths)
                    except:
                        continue
            new_file_locs[key] = new_file_list


######### CREATES THE CONTENT DICTIONARY #########

def contents_dic(spine_order, opf_soup):
    c_dict = {}
    first_result = opf_soup.find('item', id=spine_order[0])
    c_dict[0]=[0, spine_order[0], first_result['href']]
    a = 1
    for i in range(1, len(spine_order), 2):
        result1 = opf_soup.find('item', id=spine_order[i])
        if i < (len(spine_order)-1):
            result2 = opf_soup.find('item', id=spine_order[i+1])
            c_dict[a] = [i, spine_order[i], result1['href'], i+1, spine_order[i+1], result2['href']]
        else:
            c_dict[a] = [i, spine_order[i], result1['href']]
        a = a + 1
    
    return c_dict

############ MERGES PAGES INTO SPREADS  ###########

def file_merger(blank_file, c_dict, title, ind_ext_path, merged_loc, content_dir, content_ext, div_list):
    file_loc = ind_ext_path + content_dir + '/'
    for i in range(0, len(c_dict)):
        if i == 0:
            blank_soup =  load_file(blank_file)
            rfile = c_dict[i][2]
            rpage_soup = load_file(file_loc + rfile)
            c2 = extract_content(rpage_soup)
            new_soup = insert_content(blank_soup,'',c2, title)
            
        else:
            blank_soup =  load_file(blank_file)
            lfile = c_dict[i][2]
            try:
                rfile = c_dict[i][5]
                lpage_soup = load_file(file_loc + lfile)
                rpage_soup = load_file(file_loc + rfile)
                c1 = extract_content(lpage_soup)
                c2 = extract_content(rpage_soup)
                new_soup = insert_content(blank_soup,c1,c2, title)
            except:
                lpage_soup = load_file(file_loc + lfile)
                c1 = extract_content(lpage_soup)            
                new_soup = insert_content(blank_soup,c1,'', title)
        new_soup = find_textmag(div_list, new_soup)
        new_soup = str(new_soup)
        if i < 10:
            a = '00' + str(i)
        elif i < 100:
            a = '0' +str(i)
        else:
            a = str(i) 
        if i == 0:
            file_name = 'cover' + content_ext
        else:
            file_name = 'page_' + str(a) + content_ext
        c_dict[i].append(file_name)
        file = codecs.open(merged_loc + file_name, 'w', 'utf-8')
        for line in new_soup:
            file.write(line)
        file.close()
        
def insert_content(blank_soup, c1, c2, title):
    if c2 is not '':
        result = blank_soup.body.find(attrs = {'class': 'pgl'})
        result.insert(0,c1)
        result2 = blank_soup.body.find(attrs = {'class': 'pgr'})    
        result2.insert(0,c2)
    elif c1 is '':
        result = blank_soup.body.find(attrs = {'class': 'pgr'})
        result.insert(0,c1)
    else:
        result2 = blank_soup.body.find(attrs = {'class': 'pgl'})
        result2.insert(0,c1)
    blank_soup.title.insert(0,title)
    return blank_soup

def extract_content(content_file):
    result = content_file.body.find()
    return result

def find_textmag(div_list, content): #finds text mag boxes by class on surrounding div, inserts required structure and target divs. Div IDs saved to div_list
    div_finder = re.compile('pg_[0-9]*_mag_[0-9]*')
    divs = content.findAll(attrs = {'class': div_finder})
    if len(divs) > 1:
        for a in range(len(divs)):
            div_id = str(divs[a]['class'])
            div_list.append(re.sub("[\['|'\]]", '', div_id))
            insertion_point = divs[a]
            target_insertion = content.find('body')
            sourceID = insertion_point['class'][0]
            targetID = sourceID + '_target'
            ordinal = a + 1
            inner_div = content.new_tag("div", id = sourceID)
            json_tag = content.new_tag("a")
            json_tag['class'] = 'app-amzn-magnify'
            json_tag['data-app-amzn-magnify'] = '{"targetId":"' + targetID + '", "sourceId":"' + sourceID + '", "ordinal":' + str(ordinal) + '}'
            wrap(insertion_point.contents[1], inner_div)
            wrap(insertion_point.contents[1], json_tag)
            target_div = content.new_tag("div", id = targetID,)
            target_div['class'] = 'mag_box'
            target_insertion.append(target_div)
    return content

########### END MERGER CODE ###############

########### MOVER CODE: Deletes old content files, moves new files ###########

def mover_shaker(c_dict, merged_loc, ind_ext_path, content_dir, content_root):
    file_loc = ind_ext_path + content_dir + '/'
    for i in range(0, len(c_dict)):
            if i == 0:
                name = file_loc + c_dict[i][2]
                os.remove(name)
                shutil.move(merged_loc + c_dict[i][-1], file_loc + content_root + '/')               
            else:
                try:
                    name1 = file_loc + c_dict[i][2]
                    name2 = file_loc + c_dict[i][5]
                    os.remove(name1)
                    os.remove(name2)
                    shutil.move(merged_loc + c_dict[i][-1], file_loc + content_root + '/')
                except:
                    name = file_loc + c_dict[i][2]
                    os.remove(name)
                    shutil.move(merged_loc + c_dict[i][-1], file_loc + content_root + '/')
    
########### OPF CONTENT EDITOR #############

def opf_content_editor(c_dict, opf_soup, content_loc, cover_name, title, content_root):
    #opf_soup.find(attrs = {'id': cover_name }).extract()
    title_tag = opf_soup.find('dc:title')
    title_tag.string = title
    result =  opf_soup.findAll(attrs = {'media-type': "application/smil+xml"})
    for i in result:
        i.extract()
        
    result = opf_soup.findAll('itemref')
    for i in result:
        i.extract()
       
    for i in range(0, len(c_dict)):
        if i < 10:
            a = '00' + str(i)
        elif i < 100:
            a = '0' +str(i)
        else:
            a = str(i)
        insertion_point = opf_soup.manifest
        spine_insertion = opf_soup.spine
        new_id = "page" + a
        new_href = content_root + '/' + c_dict[i][-1]
        if i == 0:
            cond1 = c_dict[i][1]
            opf_soup.find(attrs = {'id': cond1 }).extract()     
            new_tag = opf_soup.new_tag("item", id = cond1, href=new_href)
            new_tag['media-type'] = "application/xhtml+xml"
            insertion_point.append(new_tag)
            new_tag = opf_soup.new_tag('itemref', idref = cond1)
            
            spine_insertion.append(new_tag)
            try:
                result = opf_soup.find(attrs={'type':'cover'})
                result['href'] = new_href
            except:
                print('You have no guide item with the type "cover"\n')
        else:
            try:
                cond1 = c_dict[i][1]
                cond2 = c_dict[i][4]
                opf_soup.find(attrs = {'id': cond1 }).extract()
                opf_soup.find(attrs = {'id': cond2 }).extract()
                new_tag = opf_soup.new_tag("item", id = new_id, href=new_href)
                new_tag['media-type'] = "application/xhtml+xml"
                insertion_point.append(new_tag)
                new_tag = opf_soup.new_tag('itemref', idref='page'+ a)
                spine_insertion.append(new_tag)
            except:
                cond1 = c_dict[i][1]
                new_tag = opf_soup.new_tag("item", id = new_id, href=new_href)
                new_tag['media-type'] = "application/xhtml+xml"
                insertion_point.append(new_tag)
                opf_soup.find(attrs = {'id': cond1 }).extract()
                new_tag = opf_soup.new_tag('itemref', idref='page'+ a)
                spine_insertion.append(new_tag)
    try:
        result = opf_soup.find(attrs={'type':'text'})
        result['href'] = content_root + '/' + c_dict[1][-1]
    except:
        print('You have no guide item with the type "text"\n')
    return opf_soup

########## CSS INSERTER ###########

def css_inserter(height, width, ind_ext_path, style_loc, div_list):
    width = int(width)/2
    div_css = ("\n.pgl{height:" + height + "px;width:" + str(width) + "px;position:absolute;top:0;left:0;}\n.pgr{height:" + height + "px;width:" + str(width) + "px;position:absolute;top:0;left:" + str(width) + "px;}")
    mag_boxes = "\n.mag_box{position:absolute; background-color:white; border:black 3px solid; border-radius:25px; padding:10px; display:none;}"
    css = div_css + mag_boxes
    stylesheets = os.listdir(ind_ext_path + style_loc)
    if len(stylesheets) == 1:
        stylesheet_loc = ind_ext_path + style_loc + '/' + stylesheets[0]
        gotCSS = getCSS(stylesheet_loc)
        newcss = amendCSS(gotCSS, div_list)
        apendCSS(newcss, css, stylesheet_loc)
        print('Looks like you don\'t have a reset stylesheet. You should add one afterwards!')
    else:
        for sheet in stylesheets:
            if sheet != 'reset.css':
                stylesheet_loc = ind_ext_path + style_loc + '/' + sheet
                gotCSS = getCSS(stylesheet_loc)
                newcss = amendCSS(gotCSS, div_list)
                apendCSS(newcss, css, stylesheet_loc)
                print('The new css was written in the file called: ', sheet, '\nIf this wasn\'t what you wanted, perhaps you have too many stylesheets?\n')
                break
            else:
                continue
            
def getCSS(stylesheet_loc):
    finder = re.compile('.*{')
    style_dict = {}
    file = open(stylesheet_loc)
    stylesheet = file.read()
    styled = (format(stylesheet.replace("\n", "")))
    stylelist = list(re.sub(r'\s\s|\t', '', styled))
    for index in range(len(stylelist)):
        if stylelist[index] in ("{", "}"):
            stylelist.insert(index + 1, "$")
    styles = ''.join(stylelist).split('$')
    for index in range(len(styles)):
        if re.search(finder, styles[index]):
            styles[index] = re.sub('{', '', styles[index])
            style_dict[styles[index]] = styles[index + 1]
    for key, value in style_dict.items():
        values = value.split(';')
        for index in range(len(values)):
            if re.search('}', values[index]):
                values.remove(values[index])
        style_dict[key] = values
    return style_dict

def amendCSS(css, div_list):
    newcss = {}
    for id in div_list:
        div_finder = re.compile('\.' + id)
        for key, value in css.items():
            if re.search(div_finder, key):
                class_to_id = re.sub('\.', '#', key)
                newcss[re.sub("\s", '', class_to_id) + '_target'] = css[key]
    for key, value in newcss.items():
        for a in range(len(newcss[key])):
            attr = newcss[key][a]
            if re.search('top', attr):
                attr = topleft('top', attr, key)
                newcss[key][a] = attr
            if re.search('left', attr):
                attr = topleft('left', attr, key)
                newcss[key][a] = attr
            if re.search('font-size', attr):
                attr = fontsizing(attr, key)
                newcss[key][a] = attr
    return newcss

def apendCSS(newcss, css, stylesheet_loc):
    with codecs.open(stylesheet_loc, mode='a', encoding = 'UTF-8') as style_soup:
        for key, value in newcss.items():
            styles = (';\n'.join(value)) + ';'
            new_css_line = '\n' + key + ' {\n' + styles + '\n}\n'
            style_soup.write(new_css_line)
        style_soup.write(css)
        style_soup.close()

def fontsizing(attr, key): #Multiplies font-size by 2
    fs = attr.split(':')
    fsm = re.sub('em', '', fs[1])
    fsf = float(fsm)
    if fsf * 2 > 4:
        print('Warning: the text in the div with id ' + key + ' is going to appear over 4ems in height. You may need to amend.')
    new_fs = str(round(fsf * 2)) + 'em'
    fs[1] = new_fs
    attr = ':'.join(fs)
    return attr
        
def topleft(direc, attr, key): #Subtracts 2% from top/length styles
    direc = attr.split(':')
    direcm = re.sub('%', '', direc[1])
    direcf = float(direcm)
    if direcf - 5 < 0:
        print('Warning: the target div with id ' + key + ' is going to appear off the screen. You will need to amend.')
    new_direc = str(round(direcf - 2)) + '%'
    direc[1] = new_direc
    attr = ':'.join(direc)
    return attr
                
######## MISC STUFF ############

#LOADS A FILE INTO BEAUTIFUL SOUP
        
def load_file(file_loc):
    a_content_file = codecs.open(file_loc, mode='r', encoding = 'UTF-8')
    text = a_content_file.read()
    a_content_file.close()
    output = BeautifulSoup(''.join(text))
    return output
    
#REMOVE DIRECTORY
def remove_directory(path, pattern):
    for each in os.listdir(path):
        if pattern.search(each):
            name = os.path.join(path, each)
            try: 
                os.remove(name)
            except:
                None 

def remove_files_in_dir(path, pattern):
    for each in os.listdir(path):
        try:
            if pattern.search(each):
                name = os.path.join(path, each)
                os.remove(name)

        except:
            break

#FILE OVERWRITER
def overwrite_files(file_name, ind_ext_path):
    src = file_name
    dst = ind_ext_path
    shutil.move(src, dst) 
    
       
#DIRECTORY MAKER
def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST:
            pass
        else: raise
        
#CONTENT WRAPPER
def wrap(to_wrap, wrap_in):
    contents = to_wrap.replace_with(wrap_in)
    wrap_in.append(contents)
        
if __name__ == "__main__": main()