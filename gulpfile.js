'use strict';

const gulp = require('gulp'),
    htmlmin = require('gulp-htmlmin'),
    removeHtmlComments = require('gulp-remove-html-comments'),
    less = require('gulp-less'),
    path = require('path'),
    sourcemaps = require('gulp-sourcemaps'),
    cleanCSS = require('gulp-clean-css'),
    imagemin = require('gulp-imagemin'),
    concat = require('gulp-concat'),
    uglify = require('gulp-uglify'),
    babel = require('gulp-babel'),
    del = require('del'),
    autoprefixer = require('gulp-autoprefixer');

const paths = {
    styles: './src/styles/main.less',
    allstyle: './src/styles/**/*less',
    scripts: './src/js/**/*.js',
    images: './src/img/**/*',
    html: './src/templates/**/*.html'
};

gulp.task('clean', function() {
    return del(['./static/img']);
});

gulp.task('less', function () {
    return gulp.src(paths.styles)
        .pipe(sourcemaps.init())
        .pipe(less({
            paths: [path.join(__dirname, 'less', 'includes')]
        }))
        .pipe(autoprefixer({
            browsers: ['last 2 versions'],
            cascade: false
        }))
        .pipe(cleanCSS())
        .pipe(sourcemaps.write())
        .pipe(gulp.dest('./static/css'));
});

gulp.task('scripts', function() {
    return gulp.src(paths.scripts)
        .pipe(babel({
            presets: ['es2015']
        }))
        .pipe(gulp.dest('./static/'));
});

gulp.task('images', ['clean'], function() {
    return gulp.src(paths.images)
    // .pipe(imagemin({optimizationLevel: 7}))
        .pipe(gulp.dest('./static/img/'));
});

gulp.task('html', function() {
    return gulp.src(paths.html)
        .pipe(removeHtmlComments())
        .pipe(htmlmin({collapseWhitespace: true}))
        .pipe(gulp.dest('./templates/'))
        .pipe(reload({ stream:true }));
});

gulp.task('watch', function () {
    gulp.watch(paths.allstyle, ['less']);
    gulp.watch(paths.scripts, ['scripts']);
    gulp.watch(paths.html, ['html']);
});

gulp.task('default', 'watch');
