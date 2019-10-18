from __future__ import print_function
import httplib, urllib, sys, json, re, os, requests

#check if dev or prod mode
mode = sys.argv[1]

#load config from file
f = open('automin_config.json', 'r')
config = json.loads(f.read())
f.close()

total_files = len(config['files'])
files_done = 0
dev_path = {
    "js": config['path']['js']['dev'],
    "css": config['path']['css']['dev']
}

min_path = {
    "js": config['path']['js']['min'],
    "css": config['path']['css']['min']
}

html_path = config['path']['root']
for h in config['files']:
    files = {
        "js": [],
        "css": []
    }
    html_name = h['name']

    #read php file
    f = open("{}/{}".format(html_path, html_name), 'r')
    file_php = f.read()
    f.close()

    changes = {
        "js": False,
        "css": False
    }
    for k in ['css', 'js']:

        if mode == 'prod':
            #move file to min folder
            from_path = '{}/{}/{}.min.{}'.format(html_path, dev_path[k], html_name.split('.')[-2], k)
            dest_path = '{}/{}/{}.min.{}'.format(html_path, min_path[k], html_name.split('.')[-2], k)
            if os.path.isfile(from_path):
                os.rename(from_path, dest_path)

            #insert prod script/link tag if does not exist
            if k == 'js':
                pattern = r'<script src=\"{}\/{}\.min\.js\"><\/script>'.format(min_path[k], html_name.split('.')[-2])
            else:
                pattern = r'<link rel=\'stylesheet\' href=\"{}\/{}\.min\.css\"\/>'.format(min_path[k], html_name.split('.')[-2])
            
            if not re.search(pattern, file_php):
                #look for first dev file to know where to append prod
                name = h[k]['files'][0]['name']

                if k == 'js':
                    pattern = r'<script[\w\s\=\-\/\"\']*?src=[\'\"]{}\/{}[\'\"][\w\s\=\-\/\"\'>]+?<\/script>'.format(min_path[k], name)
                    replace = "<script src=\"{}/{}.min.js\"></script>\n\t<script src=\"{}/{}\"></script>".format(min_path[k], html_name.split('.')[-2], min_path[k], name)
                else:
                    pattern = r'<link[\w\s\=\-\/\"\']*?href=[\'\"]{}\/{}[\'\"]\/>'.format(min_path[k], name)
                    replace = "<link rel='stylesheet' href=\"{}/{}.min.css\"/>\n\t<link rel='stylesheet' href=\"{}/{}\"/>".format(min_path[k], html_name.split('.')[-2], min_path[k], name)

                file_php = re.sub(pattern, replace, file_php)
            
            #cut permission to dev dir
            os.system("chmod 000 {}/{}".format(html_path, dev_path[k]))

        for j in h[k]['files']:
            name = j['name']

            if mode == 'prod':     
                #check if there are changes in dev file
                from_path = '{}/{}/{}'.format(html_path, min_path[k], name)
                if not os.path.isfile(from_path):
                    from_path = '{}/{}/{}'.format(html_path, dev_path[k], name)
                dev_time = os.path.getmtime(from_path)
                if os.path.isfile('{}/{}/{}.min.{}'.format(html_path, min_path[k], html_name.split('.')[-2], k)):
                    prod_time = os.path.getmtime('{}/{}/{}.min.{}'.format(html_path, min_path[k], html_name.split('.')[-2], k))
                    if dev_time > prod_time:
                        changes[k] = True
                else:
                    changes[k] = True

                #move files to dev folder
                from_path = '{}/{}/{}'.format(html_path, min_path[k], name)
                dest_path = '{}/{}/{}'.format(html_path, dev_path[k], name)
                if os.path.isfile(from_path):
                    os.rename(from_path, dest_path)

                #store js/css files to compile later
                f = open("{}/{}/{}".format(html_path, dev_path[k], name), 'r')
                files[k].append(f.read())
                f.close()

                #erase dev script/link tags
                if k == 'js':
                    pattern = r'<script[\w\s\=\-\/\"\']*?src=[\'\"]{}\/{}[\'\"][\w\s\=\-\/\"\'>]+?<\/script>[\s]*'.format(min_path[k], name)
                else:
                    pattern = r'<link[\w\s\=\-\/\"\']*?href=[\'\"]{}\/{}[\'\"]\/>[\s]*'.format(min_path[k], name)

                file_php = re.sub(pattern, '', file_php)

            if mode == 'dev':
                #insert dev script/link tags
                if k == 'js':
                    pattern = r'<script src=\"{}\/{}\.min\.js\"><\/script>'.format(min_path[k], html_name.split('.')[-2])
                    replace = "<script src=\"{}/{}\"></script>\n\t<script src=\"{}/{}.min.js\"></script>".format(min_path[k], name, min_path[k], html_name.split('.')[-2])
                else:
                    pattern = r'<link rel=\'stylesheet\' href=\"{}\/{}\.min\.css\"\/>'.format(min_path[k], html_name.split('.')[-2])
                    replace = "<link rel='stylesheet' href=\"{}/{}\"/>\n\t<link rel='stylesheet' href=\"{}/{}.min.css\"/>".format(min_path[k], name, min_path[k], html_name.split('.')[-2])

                file_php = re.sub(pattern, replace, file_php)

                #move files to min folder
                from_path = '{}/{}/{}'.format(html_path, dev_path[k], name)
                dest_path = '{}/{}/{}'.format(html_path, min_path[k], name)
                if os.path.isfile(from_path):
                    os.rename(from_path, dest_path)


        if mode == 'dev':
            #erase prod script/link tag
            if k == 'js':
                pattern = r'<script src=\"{}\/{}\.min\.js\"><\/script>'.format(min_path[k], html_name.split('.')[-2])
            else:
                pattern = r'<link rel=\'stylesheet\' href=\"{}\/{}\.min\.css\"\/>'.format(min_path[k], html_name.split('.')[-2])

            file_php = re.sub(pattern, '', file_php)

            #move file to dev folder
            from_path = '{}/{}/{}.min.{}'.format(html_path, min_path[k], html_name.split('.')[-2], k)
            dest_path = '{}/{}/{}.min.{}'.format(html_path, dev_path[k], html_name.split('.')[-2], k)
            if os.path.isfile(from_path):        
                os.rename(from_path, dest_path)



    if mode == 'prod':
        perc = float(files_done) / total_files * 20
        print("[", end='')
        for i in range(int(perc)):
            print("=", end='')
        print("{}".format(int(perc*5)%10), end='')
        for i in range(19 - int(perc)):
            print(" ", end='')
        print("] {:.1f}%".format(perc*5))

        if changes['js']:
            data_path = "{}/{}/{}.min.js".format(html_path, min_path['js'], html_name.split('.')[-2])
            print("Building {}...".format(data_path), end='')

            # Define the parameters for the POST request and encode them in
            # a URL-safe format.
            p_array = [
                ('compilation_level', 'SIMPLE_OPTIMIZATIONS'),
                ('output_format', 'text'),
                ('output_info', 'compiled_code'),
            ]
            for file in files['js']:
                p_array.append(('js_code', "{}".format(file)))

            params = urllib.urlencode(p_array)

            # Always use the following value for the Content-type header.
            headers = { "Content-type": "application/x-www-form-urlencoded" }
            conn = httplib.HTTPSConnection('closure-compiler.appspot.com')
            conn.request('POST', '/compile', params, headers)
            response = conn.getresponse()
            data = response.read()
            
            #write bundled minified file
            f = open(data_path,"w")
            f.write(data)
            f.close()

            print("DONE")

            #print data
            conn.close()
        else:
            print("No changes for {}/{}.min.js. Skipping.".format(min_path['js'], html_name.split('.')[-2]))

        if changes['css']:
            data_path = "{}/{}/{}.min.css".format(html_path, min_path['css'], html_name.split('.')[-2])
            print("Building {}...".format(data_path), end='')

            content = ""
            for file in files['css']:
                content = content + file

            url = 'https://cssminifier.com/raw'
            data = {'input': content}
            out = requests.post(url, data=data).text

            f = open(data_path,"w")
            f.write(out)
            f.close()
            print("DONE")
        else:
            print("No changes for {}/{}.min.css. Skipping.".format(min_path['css'], html_name.split('.')[-2]))

        files_done = files_done + 1

    #write new php file
    f = open("{}/{}".format(html_path, html_name), 'w')
    f.write(file_php)
    f.close()

            

print("Mode set to {}".format(mode))
    