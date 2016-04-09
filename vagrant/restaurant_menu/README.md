This project uses gulp so this are the steps needed to install everything if some new styling is needed.

# Prerequisites: #
* npm

# Installation: #
1.Install gulp: 
```
#!unix

sudo npm install --global gulp
```


2.Install the plugins:
```
#!unix

sudo npm install gulp-watch gulp-sass gulp-clean-css gulp-rename gulp-gzip gulp-livereload

```

3. Launch gulp:
```
#!unix

gulp watch
```

This will override the file 'static/styles/styles.css' with the contents of the compiled sass code from the 'sass/main.scss' file.

4. To activate the live reload functionality just add the following script to the html:
```
#!html

<script src="//localhost:35729/livereload.js"></script>
```