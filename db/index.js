var oracledb = require('oracledb');
var express = require('express');
var bodyParser = require('body-parser')
var app = express();

// Middleware
app.use( bodyParser.json() );       // to support JSON-encoded bodies
app.use(bodyParser.urlencoded({     // to support URL-encoded bodies
  extended: true
})); 

function run_query(user, password, alias, query, success, fail) {
  console.log('run_query');
  console.log(user, password, alias, query);
  oracledb.getConnection(
    {
      user          : user,
      password      : password,
      connectString : alias,
    })
    .then(function(connection) {
      return connection.execute(query)
        .then(function(result) {
          connection.release();
          response = toObject(result.metaData, result.rows)
          console.log(response);
          success(response);
        })
        .catch(function(err) {
          console.log(err.message);
          connection.release();
          fail();
        });
    })
    .catch(function(err) {
      console.error(err.message);
      fail();
    });
}

function toObject(header, rows) {
  var result = [];
  for (var j = 0; j < rows.length; ++j){
    var rv = {};
    for (var i = 0; i < rows[j].length; ++i)
      rv[header[i].name.toLowerCase()] = rows[j][i];
    result.push(rv);
  }
  return result;
}

app.get('/', function(req, res) {
  res.send('DB connection happily listening on port 8080!')
});

app.post('/query', function (req, res) {
  console.log(req.body);
  run_query(req.body.user, req.body.password, req.body.alias, req.body.query,
    function(result) {
      console.log('success');
      res.json(result);
    }, function() {
      console.log('fail');
    });
  res.json([{'col1': 1, 'col2': 1}, {'col1': 2, 'col2': 2}]);
  console.log();
});

app.post('/execute', function (req, res) {
  console.log(req.body);
  run_query(req.body.user, req.body.password, req.body.alias, req.body.query,
    function() {
      console.log('success');
      res.json(result);
    }, function() {
      console.log('fail');
    });
  res.json([{coluna1: 1, coluna2: 1}, {coluna1: 2, coluna2: 2}]);
  console.log();
});

app.listen(8080, function () {
  console.log('DB connection happily listening on port 8080!');
});

