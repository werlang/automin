# Automin
A simple switch between dev and prod mode for your server

Automin reads the web pages in your server, and automatically creates a bundled and minified version of all the javascript and stylesheet files in **script** and **link** tags from the given page.
After that Automin modify your pages to reference the compressed files, while putting the originals in a protected dev folder.

With a simple command Automin can switch between dev and prod mode, changing the pages' references from original uncompressed files to bundled and minified version of those files. It keeps track of original files changed since the last switch to know when to re-bundle those files again. When in prod mode, the original files remain safe in the designated folder where nobody has permission to access them.

## Minify? Bundle? Why?

A minified code is removed from any whitespace, tabs and new lines. The reason to do that is to make your files a little smaller, saving bandwitch for the user. Tools like [Closure compiler](https://developers.google.com/closure/compiler) take a step further making some optimizations like changin variable names and stuff. Besides all that, it makes your code a little more obscure, and while it is by no means a security measure, it makes a little more difficult for others (users) to peek and understand your code.

Bundling is taking several files and merge them making a single larger file. It is a good practice to replace many script or link tags in your pages for a single bundled file because each of those tags make a single request to the server, while the larger bundled file represents a single request.

While developing, writing a single monolithic file is agains good practice. Writing minified code though not impossible, is extremly counter-productive. For adressing those questions, many tools were developed to create those kind of files from our source codes, but most of them require us to manually upload each file, or copy-paste the code. Even worse, keeping control of every page, editing them to reference original files or minified versions is hell.

So, facing those problems, I created Automin, mainly to use in my own development routine. It is small, does not require you to install anything (except python, which most servers already have) and easy to use. Give it a try.

## Install
There is no install, simply copy `automin.py` to any place in your server.

## Configure
Automin use the file `automin_config.json` to know where your files are located. You can create your own or feel free to copy from the rep to follow the example.

The json have two properties:

### path

Is where you will inform the location of your files, the dev and min folders.
*root* is the **absolute** path to where all your files are contained.
Inside *js* and *css* there are *dev* and *min* properties.
Inside dev will be the relative path to **root** where you will place your original files, and inside min the bundled minified files destined to prod mode.

### files

Here we will put the list of pages Automin will search for. The *name* property will contain the name of the page.
Inside *js* and *css* there is a porperty named *files*. Inside files you will find a property *name*, containing the name of the script/stylesheet the page has a reference and which you would like Automin to replace.
Note that you can leave some scripts outside of Automin sight, like CDN links to external libraries. Just dont mention them here and Automin will ignore it.

```
{
    "path": {
        "root": "/home/server/public_html",
        "js": {
            "dev": "script/dev",
            "min": "script"
        },
        "css": {
            "dev": "css/dev",
            "min": "css"
        }
    },
    "files": [{
        "name": "index.php",
        "js": {
            "files": [
                {"name": "index.js"},
                {"name": "login.js"},
                {"name": "header.js"}
            ]
        },
        "css": {
            "files": [
                {"name": "index.css"},
                {"name": "header.css"}
            ]
        }
    },{
        "name": "docs.php",
        "js": {
            "files": [
                {"name": "docs.js"},
                {"name": "side-menu.js"},
                {"name": "header.js"}
            ]
        },
        "css": {
            "files": [
                {"name": "docs.css"},
                {"name": "header.css"},
                {"name": "code.css"},
            ]
        }
    }]
}
```

## Usage

You can call Automin in the terminal:
```
python automin.py dev
```

or

```
python automin.py prod
```

By calling the **dev** argument, Automin will look for your page, remove all tags referencing files with .min.js and .min.css extension (included in automin_config.json) in the js/min and css/min folders, and replace with the files from js/dev and css/dev folders.

### Example

Assuming we have `index.php` with the following head tag:

```
<head>
	<link rel="icon" type="image/gif" href="my_icon.png" />
	<title>Index test page</title>
	
	<link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Roboto:300,400,500,700" type="text/css"/>
	
	<link rel='stylesheet' href="css/index.min.css"/>
	
	<script src='https://code.jquery.com/jquery-3.4.1.min.js'></script>
	<script src='https://code.jquery.com/ui/1.12.1/jquery-ui.min.js'></script>
	
	<script src="script/index.min.js"></script>
</head>
```

If I call:
```
python automin.py dev
```
And I am using the `automin_config.json` provided in the samples, the same page will look this way after the command:

```
<head>
	<link rel="icon" type="image/gif" href="my_icon.png" />
	<title>Index test page</title>
	
	<link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Roboto:300,400,500,700" type="text/css"/>
	
	<link rel='stylesheet' href="css/dev/index.css"/>
	<link rel='stylesheet' href="css/dev/header.css"/>
	
	<script src='https://code.jquery.com/jquery-3.4.1.min.js'></script>
	<script src='https://code.jquery.com/ui/1.12.1/jquery-ui.min.js'></script>
	
	<script src="script/dev/index.js"></script>
	<script src="script/dev/login.js"></script>
	<script src="script/dev/header.js"></script>
</head>
```

So, if your original files are inside js/dev and css/dev they can now be directly edited and your page will link them. You can see the result of the changes you make on those files just refreshing your browser.

## Bundling and Minifying

Automin when set to prod mode automatically calls external APIs to make you code smaller. So, when calling:

```
python automin.py prod
```
Automin will look on all those dev files, and compare with the min files. If there was any change in them (Automin checks are based on last change date), it flags those files to update.
Even if a single file in the list was updated, Automin need to remake the entire bundle.

### Example

For example, if only `login.js` was modified, when **prod ** argument is called, Automin will take `index.js`, `login.js` and `header.js` to create a new single file, `index.min.js`. This new file will contain the compressed version of those three files.

So after the call, our page, `index.php`, will look like:

```
<head>
	<link rel="icon" type="image/gif" href="my_icon.png" />
	<title>Index test page</title>
	
	<link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Roboto:300,400,500,700" type="text/css"/>
	
	<link rel='stylesheet' href="css/index.min.css"/>
	
	<script src='https://code.jquery.com/jquery-3.4.1.min.js'></script>
	<script src='https://code.jquery.com/ui/1.12.1/jquery-ui.min.js'></script>
	
	<script src="script/index.min.js"></script>
</head>
```

After all that, Automin will change the permission of the dev folders (js and css) to 000, making any files inside it unreachable to the website users. It is the way Automin ensures your dev folder is protected, and is only reached when the server is in dev mode.

## External APIs

To minify all your files, Automin use calls to external APIs.
- [Closure Compiler API](https://developers.google.com/closure/compiler) for javascript minification.
- [CSS Minifier API](https://cssminifier.com/) for css minification.

## Final Remarks
I hope you make good use of Automin. I enjoyed writing it and I like the fact it is a simple solution only requiring copying a single python script and creating a config file.
Enjoy!

## Author
Pablo Werlang - [pswerlang@gmail.com](mailto:pswerlang@gmail.com)
Check out my other project, [gladCode](https://gladcode.tk) (in Portuguese).
