

const webpack = require('webpack')
const webpackDevMiddleware = require('webpack-dev-middleware')
const webpackHotMiddleware = require('webpack-hot-middleware')
const config = require('../webpack.config.js')
const compiler = webpack(config)
const express = require("express")
const path = require("path")




const app = express();


app.use(express.static(__dirname + '../dist'));
app.use(webpackDevMiddleware(compiler));
app.use(webpackHotMiddleware(compiler)); // And this line
app.get('/', function response(req, res) {
    res.sendFile(path.join(__dirname, '../index.html'));
});
// Test app
app.get('/graphCuts', function response(req, res) {
    //res.send("Welcome")

    // Use child_process.spawn method from 
    // child_process module and assign it
    // to variable spawn
    var spawn = require("child_process").spawn;
     
    // Parameters passed in spawn -
    // 1. type_of_script
    // 2. list containing Path of the script
    //    and arguments for the script 
     
    // E.g : http://localhost:3000/name?firstname=Mike&lastname=Will
    // so, first name = Mike and last name = Will
    var process = spawn('python3',[__dirname+"/main.py",
				  req.query.image] );
 
    // Takes stdout data from script which executed
    // with arguments and send this data to res object
    process.stdout.on('data', function(data) {
	console.log(data.toString())
	//res.send(data.toString());
    } )
    process.stderr.on('data', function(data) {
	errMsg = "Server Err: " + data.toString()
	console.log(errMsg)
	//res.send(errMsg)
    } )
    process.on("close", function() {	
    })
    data = JSON.parse(req.query.image)
    process.stdin.write(JSON.stringify(data));
    process.stdin.end();
});

app.listen(8080)

