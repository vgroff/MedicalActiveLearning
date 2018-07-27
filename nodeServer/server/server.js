

const webpack = require('webpack')
const webpackDevMiddleware = require('webpack-dev-middleware')
const webpackHotMiddleware = require('webpack-hot-middleware')
const config = require('../webpack.config.js')
const compiler = webpack(config)
const express = require("express")
const path = require("path")
const bodyParser = require('body-parser');



const app = express();


app.use(express.static(__dirname + '../dist'));
app.use(webpackDevMiddleware(compiler));
app.use(webpackHotMiddleware(compiler)); // And this line
app.use(express.json({limit:"500mb"}));
app.get('/', function response(req, res) {
    res.sendFile(path.join(__dirname, '../index.html'));
});
// Test app
app.post('/graphCuts', function response(req, res) {
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
    console.log("Request Received. Spawing Python process...")
    var process = spawn('python3',[__dirname+"/main.py"]);//,
				   //req.body.image,
				   //req.body.scribbles] );
 
    // Takes stdout data from script which executed
    // with arguments and send this data to res object
    var resp = ""
    process.stdout.on('data', function(data) {
	console.log(data.toString())
	var str = data.toString()
	resp += str
	var l = str.length
	console.log(str.slice(l-5, l-1), str.slice(l-5, l-1) === "Done")
	if (str.slice(l-5, l-1) === "Done") {
	    console.log("Sending: " + resp.slice(0, resp.length-5))
	    res.send(resp.slice(0, resp.length-5))
	}
	//data.toString());
    } )
    process.stderr.on('data', function(data) {
	errMsg = "Server Err: " + data.toString()
	console.log(errMsg)
	//res.send(errMsg)
    } )
    process.on("close", function() {	
    })
    
    data = JSON.parse(req.body.image)
    process.stdin.write(JSON.stringify(data) + "\n");
    data = JSON.parse(req.body.scribbles)
    process.stdin.write(JSON.stringify(data));
    process.stdin.end();
    
});

app.listen(8080)

