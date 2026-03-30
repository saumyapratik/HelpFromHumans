const express = require("express");
const path = require("path");
const mongoose = require("mongoose");

const app = express();
// Serve static files (CSS, JS, images) from views folder
app.use(express.static(path.join(__dirname, 'views')));

// Middleware
app.use(express.urlencoded({ extended: true }));
app.use(express.json());

// ---------- MongoDB Connection ----------
mongoose.connect("mongodb+srv://saumya09638_db_user:78MIsdK2RmqO4Naq@cluster0.vcbqxox.mongodb.net/HelpFromHumans?retryWrites=true&w=majority")
.then(() => console.log("MongoDB connected ✅"))
.catch(err => console.log("MongoDB ERROR ❌", err));

// ---------- Schemas ----------

// User Schema
const userSchema = new mongoose.Schema({
    username: String,
    email: String,
    password: String
});
const User = mongoose.model("User", userSchema);

// Question Schema
const questionSchema = new mongoose.Schema({
    username: String,
    title: String,
    question: String,
    date: {
        type: Date,
        default: Date.now
    }
});
const Question = mongoose.model("Question", questionSchema);

// Answer Schema
const answerSchema = new mongoose.Schema({
    questionId: String,
    answer: String,
    date: {
        type: Date,
        default: Date.now
    }
});
const Answer = mongoose.model("Answer", answerSchema);

// ---------- ROUTES ----------

// Home
app.get("/", (req, res) => {
    res.sendFile(path.join(__dirname, "views", "index.html"));
});

// Signup page
app.get("/signup", (req, res) => {
    res.sendFile(path.join(__dirname, "views", "signup.html"));
});

// Signup
app.post("/signup", async (req, res) => {
    const { username, email, password } = req.body;

    try {
        const existingUser = await User.findOne({ email });

        if (existingUser) {
            return res.send("User already exists ❌");
        }

        const newUser = new User({ username, email, password });
        await newUser.save();

        res.send("Signup successful ✅");

    } catch (err) {
        res.send("Signup error ❌");
    }
});

// Login page
app.get("/login", (req, res) => {
    res.sendFile(path.join(__dirname, "views", "login.html"));
});

// Login
app.post("/login", async (req, res) => {
    const { email, password } = req.body;

    try {
        const user = await User.findOne({ email, password });

        if (!user) {
            return res.send("Invalid credentials ❌");
        }

        res.sendFile(path.join(__dirname, "views", "dashboard.html"));

    } catch (err) {
        res.send("Login error ❌");
    }
});

// Dashboard
app.get("/dashboard", (req, res) => {
    res.sendFile(path.join(__dirname, "views", "dashboard.html"));
});

// Ask page
app.get("/ask", (req, res) => {
    res.sendFile(path.join(__dirname, "views", "ask.html"));
});

// Save Question
app.post("/ask", async (req, res) => {
    const { title, question } = req.body;

    try {
        const newQuestion = new Question({ title, question });
        await newQuestion.save();

        res.send("Question posted ✅");

    } catch (err) {
        res.send("Error saving question ❌");
    }
});

// View all questions
app.get("/questions", async (req, res) => {
    try {
        const questions = await Question.find();

        let html = "<h1>All Questions</h1>";

        questions.forEach(q => {
            html += `
                <div style="border:1px solid black; margin:10px; padding:10px;">
                    <h3>${q.title}</h3>
                    <p>${q.question}</p>
                    <a href="/question/${q._id}">
                        <button>View & Answer</button>
                    </a>
                </div>
            `;
        });

        html += '<br><a href="/dashboard">Back</a>';

        res.send(html);

    } catch (err) {
        res.send("Error loading questions ❌");
    }
});

// Single question
app.get("/question/:id", async (req, res) => {
    try {
        const question = await Question.findById(req.params.id);
        const answers = await Answer.find({ questionId: req.params.id });

        let html = `
            <h1>${question.title}</h1>
            <p>${question.question}</p>
            <h2>Answers:</h2>
        `;

        answers.forEach(a => {
            html += `<p>• ${a.answer}</p>`;
        });

        html += `
            <h3>Add Answer</h3>
            <form action="/answer" method="POST">
                <input type="hidden" name="questionId" value="${question._id}">
                <textarea name="answer" required></textarea>
                <br><br>
                <button type="submit">Submit</button>
            </form>

            <br><a href="/questions">Back</a>
        `;

        res.send(html);

    } catch (err) {
        res.send("Error ❌");
    }
});

// Save answer
app.post("/answer", async (req, res) => {
    try {
        const { questionId, answer } = req.body;

        const newAnswer = new Answer({ questionId, answer });
        await newAnswer.save();

        res.redirect("/question/" + questionId);

    } catch (err) {
        res.send("Error saving answer ❌");
    }
});

// ---------- START SERVER ----------
const PORT = process.env.PORT || 3000;

app.listen(PORT, () => {
    console.log("HelpFromHumans Server is Running 🚀");
});