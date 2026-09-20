# 📱 IARE Bot — Complete Student Guide

Welcome to the **IARE Bot Student Guide**! This simple handbook walks you through everything you need to know about using the bot to check attendance, calculate bunks, view biometric hours, upload lab records, and track your marks directly inside Telegram.

---

## 📌 Table of Contents
1. [What Can the Bot Do for You?](#what-can-the-bot-do-for-you)
2. [Step-by-Step: Getting Started](#step-by-step-getting-started)
   - [Step 1: Start the Bot](#step-1-start-the-bot)
   - [Step 2: Log In with Your College ID](#step-2-log-in-with-your-college-id)
   - [Step 3: What If Your Password Has Spaces?](#step-3-what-if-your-password-has-spaces)
3. [Understanding the Main Menu Buttons](#understanding-the-main-menu-buttons)
   - [📊 Attendance](#-attendance)
   - [🎯 Bunk Calculator (Safe-Miss Planner)](#-bunk-calculator-safe-miss-planner)
   - [🕒 Biometric Log](#-biometric-log)
   - [💼 PAT Attendance](#-pat-attendance)
   - [📑 Lab Records (View & Upload)](#-lab-records-view--upload)
   - [🎓 Student Info (CGPA, Mid Marks, Fees)](#-student-info-cgpa-mid-marks-fees)
   - [⚙️ Saved Username & Auto-Login](#️-saved-username--auto-login)
   - [🚪 Logging Out](#-logging-out)
4. [Customizing Your Preferences (`/settings`)](#customizing-your-preferences-settings)
5. [Reporting an Issue or Asking for Help (`/report`)](#reporting-an-issue-or-asking-for-help-report)
6. [Frequently Asked Questions (FAQ)](#frequently-asked-questions-faq)

---

## What Can the Bot Do for You?

Instead of opening your browser, logging into the Samvidha portal, and navigating multiple slow pages, you can get all your college information with a single tap in Telegram:

- **Instant Attendance:** View subject-wise and overall attendance in seconds.
- **Bunk Calculator:** Know exactly how many classes you can skip without dropping below your target percentage.
- **Biometric Punch Times:** Check your daily in-time, out-time, and total hours on campus.
- **Lab Record Uploads:** Send your lab experiment PDF right in chat; if it's too large, the bot compresses it for you automatically.
- **Academic Grades & Marks:** Check your SGPA, cumulative CGPA, CIE mid marks, and fee payment receipts.

---

## Step-by-Step: Getting Started

### Step 1: Start the Bot
Open Telegram, find the bot, and click the **Start** button at the bottom of the chat (or send `/start`).
The bot will say hello and show you the basic commands.

---

### Step 2: Log In with Your College ID
To fetch your personal college data, log in using your Roll Number and Samvidha password:

```text
/login <ROLL_NUMBER> <PASSWORD>
```

**Example:**
```text
/login 21951A0501 MyPassword123
```

Once logged in, the bot will display your main action menu with buttons!

---

### Step 3: What If Your Password Has Spaces?
If your Samvidha password contains one or more spaces, put your password inside **double quotation marks (`"..."`)** or **single quotation marks (`'...'`)**:

**Example:**
```text
/login 21951A0501 "my secret password"
```
or
```text
/login 21951A0501 'my secret password'
```

---

## Understanding the Main Menu Buttons

After logging in, you will see an interactive keyboard with the following buttons:

```text
┌───────────────────────────┐
│        MAIN MENU          │
├─────────────┬─────────────┤
│ Attendance  │    Bunk     │
├─────────────┼─────────────┤
│  Biometric  │   Logout    │
├─────────────┴─────────────┤
│       Labs Records        │
├───────────────────────────┤
│       Student Info        │
├───────────────────────────┤
│      Saved Username       │
└───────────────────────────┘
```

Here is what each button does:

### 📊 Attendance
- **What it shows:**
  - Every course you are registered for this semester.
  - Number of classes conducted vs classes you attended.
  - Subject-wise attendance percentage.
  - Overall aggregate attendance percentage.

---

### 🎯 Bunk Calculator (Safe-Miss Planner)
- **What it shows:**
  - This is one of the most useful features of the bot! It compares your current attendance against your target attendance percentage (default is **75%**, but you can customize it in `/settings`).
  - **If your attendance is above 75%:**
    The bot calculates the exact number of classes you can safely miss while remaining above the threshold.
  - **If your attendance is below 75%:**
    The bot tells you exactly how many consecutive upcoming classes you must attend to pull your attendance back up to 75%.

---

### 🕒 Biometric Log
- **What it shows:**
  - Your first swipe-in time of the day.
  - Your most recent swipe-out time.
  - Total elapsed time spent on campus today.
  - Whether you have met the minimum daily hours requirement.

---

### 💼 PAT Attendance
- **What it shows:**
  - Separate attendance statistics specifically for Placement & Training (PAT) sessions and special training classes.

---

### 📑 Lab Records (View & Upload)
- **What it shows:**
  - Review your uploaded laboratory experiment files for each lab course.
- **Uploading a Lab Record PDF:**
  1. Simply send your experiment `.pdf` document to the bot in the chat.
  2. The bot will ask for the experiment title (or automatically detect it if you enabled Auto Title in `/settings`).
  3. **Automatic File Compression:** College portals often reject PDF files larger than 1MB. You don't need any third-party app—the bot automatically optimizes and compresses large PDFs so the upload goes through smoothly!
- **Deleting a Record:**
  - Tap on the uploaded record to remove it if you wish to re-upload a revised copy.

---

### 🎓 Student Info (CGPA, Mid Marks, Fees)
- Tap **Student Info** to view:
  - **Profile:** Full name, department, section, roll number, and mentor name.
  - **CGPA & SGPA:** Your semester-by-semester Grade Point Average and overall cumulative CGPA.
  - **CIE Marks:** Continuous Internal Evaluation (Mid-term) marks for current subjects.
  - **Fee Payments:** Receipts of tuition, transport, or exam fee payments and remaining balance dues.

---

### ⚙️ Saved Username & Auto-Login
- When you log in, the bot can save your roll number so you don't have to type `/login` and your password every time your session expires.
- Tap **Saved Username** to:
  - **Auto-Login:** Immediately refresh your session with 1 tap.
  - **Remove:** Delete your saved credentials from the bot whenever you want.

---

### 🚪 Logging Out
- Tap **Logout** or send the command `/logout`.
- This safely ends your active session.

---

## Customizing Your Preferences (`/settings`)

Send `/settings` to open your personal options menu:

1. **Attendance Threshold:**
   - Change your bunk calculator target (choose between **65%**, **70%**, **75%**, **80%**, or **85%**).
2. **Biometric Threshold:**
   - Customize the daily campus hours target.
3. **Title Extract (For Lab Uploads):**
   - **Auto Extract:** The bot automatically scans the first page of your PDF to find the experiment title.
   - **Manual Title:** The bot asks you to type the title for each upload.
4. **User Interface (UI Style):**
   - **Traditional UI:** Clean, compact monospace format.
   - **Updated UI:** Modern format with emoji badges, cards, and dividers.

---

## Reporting an Issue or Asking for Help (`/report`)

If you notice that your attendance isn't matching, an upload failed, or you want to request a feature, you can send a message directly to the student maintainers:

```text
/report <your issue or question here>
```

**Example:**
```text
/report Hi, my biometric out-time for today is not showing up. Could you check?
```

- **How it works:** Your message is submitted with the exact Indian time (IST).
- **Getting a reply:** When a maintainer replies, you will receive a direct notification message in Telegram with the answer!

---

## Frequently Asked Questions (FAQ)

#### Q1: Do I need to type `/login` every day?
No. Once you log in, your credentials are saved. Whenever your session expires, you can simply tap the **Saved Username** button and click **Auto-Login** to reconnect in one second.

#### Q2: What should I do if the bot says "Login Failed"?
- Check that your Roll Number is typed correctly (e.g., in capital letters).
- Verify that your password matches your Samvidha portal password.
- If your password has spaces in it, make sure you put it inside quotation marks: `/login 21951A0501 "my password with space"`.
- Sometimes the college portal goes down for maintenance late at night. If so, try again after a little while.

#### Q3: How do I change the attendance percentage for my bunk calculation?
Send `/settings` in the chat, click on **Attendance Threshold**, and select your preferred percentage (e.g., 75% or 80%). The Bunk button will instantly start using your new target!

#### Q4: How do I delete my saved login from the bot?
Click the **Saved Username** button in the main menu and press **Remove**. Your login details will be deleted immediately.

#### Q5: Who maintains this bot?
The bot is developed and maintained by students of IARE. If you have any feedback, suggestions, or need help, just use `/report <your message>`!
