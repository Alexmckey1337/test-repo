'use strict';
const path = require('path');
const webpack = require('webpack');
const ProvidePlugin = require('webpack/lib/ProvidePlugin');

const NODE_ENV = process.env.NODE_ENV || 'development';

module.exports = {
    context: path.resolve(__dirname, './src/js'),
    entry: {
        entry: ['babel-polyfill', './entry.js'],
        restorepass: ['babel-polyfill', './restorepass.js'],
        // editpass: ['babel-polyfill', './editpass.js'],
        main: ['babel-polyfill', './main.js'],
        account: ['babel-polyfill', './account.js'],
        // tickets: ['babel-polyfill', './tickets.js'],
        // add_user: './add_user.js',
        websocket: './websocket.js',
        dashboard: ['babel-polyfill', './dashboard.js'],
        // database_users: ['babel-polyfill', './database_users.js'],
        // database_churches: ['babel-polyfill', './database_churches'],
        // churches_detail: ['babel-polyfill', './churches_detail'],
        // church_reports: ['babel-polyfill', './church_reports'],
        // church_report_detail: ['babel-polyfill', './church_report_detail'],
        // church_statistics: ['babel-polyfill', './church_statistics'],
        // database_home_groups: ['babel-polyfill', './database_home_groups.js'],
        // home_groups_detail: ['babel-polyfill', './home_groups_detail'],
        // home_reports: ['babel-polyfill', './home_reports'],
        // home_reports_detail: ['babel-polyfill', './home_reports_detail'],
        // home_statistics: ['babel-polyfill', './home_statistics'],
        // all_payment: ['babel-polyfill', './all_payment'],
        // partner_payments: ['babel-polyfill', './partner_payments'],
        // deal_payments: ['babel-polyfill', './deal_payments'],
        // deals: ['babel-polyfill', './deals'],
        // partner_list: ['babel-polyfill', './partner_list'],
        // stats: ['babel-polyfill', './stats'],
        // payments: ['babel-polyfill', './payments'],
        // summit_detail: ['babel-polyfill', './summit_detail'],
        // summit_stats: ['babel-polyfill', './summit_stats'],
        // summit_bishop: ['babel-polyfill', './summit_bishop'],
    },
    output: {
        path: path.resolve(__dirname, './public/static/js'),
        filename: '[name].bundle.js',
    },

    watch: NODE_ENV == 'development',
    watchOptions: {
        aggregateTimeout: 100
    },

    devtool: NODE_ENV == 'development' ? 'source-map' : false,

    plugins: [
        new webpack.DefinePlugin({
            NODE_ENV: JSON.stringify(NODE_ENV)
        }),
        new webpack.ProvidePlugin({
            $: 'jquery',
            jQuery: 'jquery',
            _: 'lodash',
        }),
        new webpack.optimize.CommonsChunkPlugin({
            name: 'vendor',
            minChunks: 2,
            filename: 'vendor.bundle.js'
        })
    ],

    resolveLoader: {
        modules: ['node_modules'],
        moduleExtensions: ['-loader', '*'],
        extensions: ['.js']
    },

    module: {
        rules: [
            {
                test: /\.js$/,
                include: [
                    path.resolve(__dirname, "src/js")
                ],
                use: [
                    'babel-loader'
                ],
            },
            {
                test: /\.css$/,
                use: [
                    'style-loader',
                    'css-loader'
                ]
            },
            {
                test: /\.(sass|scss)$/,
                use: [
                    'style-loader',
                    'css-loader',
                    'sass-loader'
                ]
            }
        ]
    },
};

if (NODE_ENV == 'production') {
    module.exports.plugins.push(
        new webpack.optimize.UglifyJsPlugin({
            compress: {
                warnings: false,
                drop_console: true,
                unsafe: true
            }
        })
    );
}