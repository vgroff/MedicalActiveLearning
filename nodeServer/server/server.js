

const webpack = require('webpack')
const webpackDevMiddleware = require('webpack-dev-middleware')
const webpackHotMiddleware = require('webpack-hot-middleware')
const config = require('../webpack.config.js')
const compiler = webpack(config)
const express = require("express")
const path = require("path")
const bodyParser = require('body-parser');
const fs = require("fs")

ongoingJobs = []

function addJob(ongoingJobs, id) {
    job = {"id":id, "lock":false};
}


const app = express();


app.use(express.static(__dirname + '../dist'));
app.use(webpackDevMiddleware(compiler));
app.use(webpackHotMiddleware(compiler)); // And this line
app.use(express.json({limit:"500mb"}));
app.get('/', function response(req, res) {
    res.sendFile(path.join(__dirname, '../index.html'));
});
// Test app
app.post('/segment', function response(req, res) {
    req.setTimeout(0);
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

    var process = spawn('python3',[__dirname+"/CNN/main.py",
				  req.body.action]);//,
				   //req.body.image,
				   //req.body.scribbles] );
 
    // Takes stdout data from script which executed
    // with arguments and send this data to res object
    var resp = ""
    var log = ""
    var print = ""
    process.stdout.on('data', async function(data) {
	var str = data.toString()
	console.log(str)
	resp += str
	log  += str
	var l = str.length
	if (str.slice(l-5, l-1) === "Done") {
	    var start = 0
	    for (var i = 0; i < resp.length; i++) {
		print += "\n" + resp.slice(i,i+3)
		if (resp.slice(i,i+3) === "[[[") {
		    start = i
		    break
		}
	    }
	    console.log(start)
	    //console.log("Sending: " + resp.slice(0, resp.length-5))
	    res.send(resp.slice(start, resp.length-5))
	    //fs.writeFile("./respSend.txt", JSON.stringify(a))
	    //fs.writeFile("./log.txt", log)
	    //fs.writeFile("./print.txt", print)
	    //fs.writeFile("./response.txt", resp.slice(start, resp.length-5))
	    console.log("Done sending")
	}
	//data.toString());
    } )
    process.stderr.on('data', function(data) {
	errMsg = "Server Err: " + data.toString()
	log += errMsg
	console.log(errMsg)
	//res.send("Server Error occurred")
    } )
    process.on("close", function() {	
    })
    
    //data = JSON.parse(req.body.image)
    process.stdin.write(req.body.image + "\n");
    process.stdin.write(req.body.scribbles);
    process.stdin.end();
    
});


app.listen(8080)

