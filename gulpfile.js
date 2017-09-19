'use strict';

const gulp = require('gulp'),
    less = require('gulp-less'),
    path = require('path'),
    sourcemaps = require('gulp-sourcemaps'),
    cleanCSS = require('gulp-clean-css'),
    imagemin = require('gulp-imagemin'),
    concat = require('gulp-concat'),
    uglify = require('gulp-uglify'),
    babel = require('gulp-babel'),
    del = require('del'),
    autoprefixer = require('gulp-autoprefixer'),
    changed = require('gulp-changed');

const paths = {
    styles: './src/styles/**/*less',
    scripts: './src/js/**/*.js',
    images: './src/img/**/*',
    fonts: './src/fonts/**/*'
};

gulp.task('clean', function () {
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
        .pipe(gulp.dest('public/static/css/'));
});

gulp.task('images', ['clean'], function () {
    return gulp.src(paths.images)
        .pipe(imagemin({optimizationLevel: 9}))
        .pipe(gulp.dest('public/static/img/'));
});

gulp.task('font', ['clean'], function () {
    return gulp.src(paths.fonts)
        .pipe(gulp.dest('public/static/fonts/'));
});

gulp.task('watch', function () {
    gulp.watch(paths.styles, ['less']);
    gulp.watch(paths.html, ['html']);
});

gulp.task('default', ['less', 'watch']);
