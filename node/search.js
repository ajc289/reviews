var express = require('express');
var http = require('http');
var path = require('path');
var Busboy = require('busboy');
var fs = require('fs')
var app = express();
var upload_app = express();
var net = require("net");

app.use(express.bodyParser());

app.configure(function(){app.set('port', 8300)});

app.get('/', function(req, res){
   var query = req.param('query');
   console.log('post ' + query);
   var s = net.Socket();
   s.connect(9300);
   s.write (query + '\n');

   s.on('data',function(d){
      console.log(JSON.parse(String(d)));
      res.send(JSON.parse(String(d)));
      res.end();
   });

   s.end();
});

http.createServer(app).listen(app.get('port'), function(){
  console.log("Express server listening on port " + app.get('port'));
});



