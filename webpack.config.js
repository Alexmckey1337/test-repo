'use strict';
const path = require('path');
const webpack = require('webpack');
const ProvidePlugin = require('webpack/lib/ProvidePlugin');

const NODE_ENV = process.env.NODE_ENV || 'development';

module.exports = {
    context: path.resolve(__dirname, './src/js'),
    entry: {
        entry: ['babel-polyfill', './entry.js'],
        tasks: ['babel-polyfill', './tasks.js'],
        restorepass: ['babel-polyfill', './restorepass.js'],
        editpass: ['babel-polyfill', './editpass.js'],
        main: ['babel-polyfill', './main.js'],
        account: ['babel-polyfill', './account.js'],
        tickets: ['babel-polyfill', './tickets.js'],
        add_user: './add_user.js',
        websocket: './websocket.js',
        dashboard: ['babel-polyfill', './dashboard.js'],
        database_users: ['babel-polyfill', './database_users.js'],
        database_churches: ['babel-polyfill', './database_churches'],
        churches_detail: ['babel-polyfill', './churches_detail'],
        church_reports: ['babel-polyfill', './church_reports'],
        church_report_detail: ['babel-polyfill', './church_report_detail'],
        reports_summary: ['babel-polyfill', './reports_summary'],
        church_statistics: ['babel-polyfill', './church_statistics'],
        database_home_groups: ['babel-polyfill', './database_home_groups.js'],
        report_payments: ['babel-polyfill', './report_payments.js'],
        home_groups_detail: ['babel-polyfill', './home_groups_detail'],
        home_reports: ['babel-polyfill', './home_reports'],
        meetings_summary: ['babel-polyfill', './meetings_summary'],
        home_reports_detail: ['babel-polyfill', './home_reports_detail'],
        home_statistics: ['babel-polyfill', './home_statistics'],
        deals: ['babel-polyfill', './deals'],
        partner_list: ['babel-polyfill', './partner_list'],
        partnership_summary: ['babel-polyfill', './partnership_summary'],
        manager_summary: ['babel-polyfill', './manager_summary'],
        stats: ['babel-polyfill', './stats'],
        payments: ['babel-polyfill', './payments'],
        summit_detail: ['babel-polyfill', './summit_detail'],
        summit_stats: ['babel-polyfill', './summit_stats'],
        summit_bishop: ['babel-polyfill', './summit_bishop'],
        summit_statistics: ['babel-polyfill', './summit_statistics'],
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
        new webpack.ContextReplacementPlugin(/^\.\/locale$/, context => {
            if (!/\/moment\//.test(context.context)) {
                return
            }
            Object.assign(context, {
                regExp: /^\.\/(en|ru)/,
                request: '../../locale'
            })
        }),
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
        }),
        new webpack.optimize.OccurrenceOrderPlugin(),
        // new webpack.optimize.CommonsChunkPlugin({
        //     name: "vendor",
        //     minChunks: function (module) {
        //         return module.context && module.context.indexOf("node_modules") !== -1;
        //     },
        //     filename: 'vendor.bundle.js'
        // }),
        // new webpack.optimize.CommonsChunkPlugin({
        //     name: "manifest",
        //     minChunks: Infinity,
        //     filename: 'manifest.bundle.js'
        // }),
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
                    { loader: 'css-loader', options: { minimize: true } }
                ]
            },
            {
                test: /\.(sass|scss)$/,
                use: [
                    'style-loader',
                    { loader: 'css-loader', options: { minimize: true } },
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
                sequences: true,
                booleans: true,
                loops: true,
                unused: true,
                warnings: false,
                drop_console: true,
                unsafe: true
            }
        })
    );
}