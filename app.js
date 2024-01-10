const express = require("express");
const bodyParser = require("body-parser");
const ejs = require("ejs");
const Snoowrap = require('snoowrap');
const { spawn } = require("child_process");


const app = express();

app.set('view engine', 'ejs');

app.use(bodyParser.urlencoded({extended: true}));
app.use(express.static("public"));

const r = new Snoowrap({
  userAgent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
  clientId: "s5QCHe-MJMNZfCuQw4lorA",
  clientSecret: "zd8Dcioo0CxB5BcIXZQtV43Y9llr2w",
  refreshToken: "2520944493181-eeS7_6yrLPCNtHWpqUuV2jUUN9RcOw"
});

function getUserInterests(username, Nor) {
  const user = r.getUser(username).fetch();

  const promiseArray = Promise.all([
    user.getComments({ amount: Nor }),
    user.getSubmissions({ amount: Nor }),
  ]);

  const content = promiseArray.then(([comments, submissions]) => [...comments, ...submissions]);

  const interests = content.then(content => content.reduce((acc, item) => {
    const subreddit = item.subreddit.display_name;
    acc[subreddit] = (acc[subreddit] || 0) + 1;
    return acc;
  }, {}));

  const sortedInterests = interests.then(interests => Object.entries(interests).sort((a, b) => b[1] - a[1]).slice(0, Nor));
  const topInterests = sortedInterests.then(sortedInterests => sortedInterests.map(([subreddit, count]) => ({ subreddit, count })));
  
  return topInterests;
}

app.get("/", function(req, res){
  res.render("home");
});

app.post("/", async function(req, res){
  username = req.body.username;
  Nor = req.body.Nor;
  try {
    const username = req.body.username;
    const numberOfResults = parseInt(req.body.Nor);

    const topInterests = await getUserInterests(username, numberOfResults);

    res.render("result", { topInterests, username:username });
  } catch (error) {
    console.error(error);
    res.render("error", { message: "An error occurred while processing your request." });
  }
  // const python = spawn('python', ['ml.py', username, Nor]);
  // let result = '';

  // // Collect the output from ml.py
  // python.stdout.on('data', (data) => {
  //   result += data.toString();
  // });

  // // Send the result back to the frontend
  // python.on('close', (code) => {
  //   if (code !== 0) {
  //     res.send(`Error: ${code}`);
  //   } else {
  //     res.send(result);
  //   }
  // });
});

app.listen(3000, function(){
  console.log("Server is running on 3000");
});