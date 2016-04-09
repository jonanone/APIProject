var fs = require('fs');
var path = require('path');
var gulp = require('gulp');
var sass = require('gulp-sass');
var watch = require('gulp-watch');
var cleancss = require('gulp-clean-css');
var rename = require('gulp-rename');
var gzip = require('gulp-gzip');
var livereload = require('gulp-livereload');


function getFolders(dir){
    return fs.readdirSync(dir)
      .filter(function(file){
        return fs.statSync(path.join(dir, file)).isDirectory();
      });
}


// Gulp plumber error handler
var onError = function(err) {
    console.log(err);
};


/* Compile Sass */
gulp.task('sass', function() {
    gulp.src('sass/main.scss')
        .pipe(sass())
        .pipe(rename('main.css'))
        .pipe(cleancss())
        .pipe(gulp.dest('static/styles/'))
        .pipe(livereload());
});


/* Watch Files For Changes */
gulp.task('watch', function() {
    livereload.listen();
    gulp.watch('sass/*.scss', ['sass']);    

    /* Trigger a live reload on any Django template changes */
    gulp.watch('templates/*').on('change', livereload.changed);

});

gulp.task('default', ['sass', 'watch']);

gulp.task('initialize', ['sass']);