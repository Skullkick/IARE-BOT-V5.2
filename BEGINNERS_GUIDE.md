# IARE UNOFFICIAL Bot — Student User Guide

This guide outlines the features and commands available to students using the IARE Unofficial Telegram Bot. It provides step-by-step instructions for checking attendance, planning classes, viewing biometric logs, managing lab records, and tracking academic progress directly via Telegram.

---

## Table of Contents

1. [Overview](#overview)
2. [Getting Started](#getting-started)
   - [Starting the Bot](#starting-the-bot)
   - [Logging In](#logging-in)
   - [Passwords with Spaces](#passwords-with-spaces)
3. [Main Menu Navigation](#main-menu-navigation)
   - [Attendance](#attendance)
   - [Bunk Calculator](#bunk-calculator)
   - [Biometric Log](#biometric-log)
   - [PAT Attendance](#pat-attendance)
   - [Lab Records](#lab-records)
   - [Student Info](#student-info)
   - [Saved Username](#saved-username)
   - [Logging Out](#logging-out)
4. [User Settings](#user-settings)
5. [Help and Issue Reporting](#help-and-issue-reporting)
6. [Frequently Asked Questions](#frequently-asked-questions)

---

## Overview

The IARE Unofficial Bot integrates directly with the Samvidha student portal, allowing you to access key academic information quickly without having to log in through a web browser each time.

Key capabilities:
- Real-time subject-wise and aggregate attendance.
- Bunk calculations based on your target attendance threshold.
- Daily biometric swipe timings and total campus hours.
- Lab record document uploads with automatic compression for large files.
- Internal evaluation marks, semester SGPA, and cumulative CGPA.
- Direct reporting channel to student maintainers.

---

## Getting Started

### Starting the Bot

1. Open Telegram and search for the bot handle.
2. Press the **Start** button at the bottom of the chat window or send the command:
   ```text
   /start
   ```
3. The bot will return a welcome message confirming that your session is active.

### Logging In

To access your student records, authenticate using your college roll number and Samvidha password:

```text
/login <ROLL_NUMBER> <PASSWORD>
```

**Example:**
```text
/login 21951A0501 MyPassword123
```

Upon successful authentication, the bot will ask:
> *"If you want to save your credentials Click on 'Yes'."*

- **If you click "Yes":** Your credentials will be saved. Whenever your session expires, the bot will **automatically re-log you in in the background** when you press any button (such as Attendance, Bunk, or Biometric) without requiring any manual action.
- **If you click "No" (or skip):** Your credentials will not be stored. Once your temporary session expires, you must log in again using `/login <ROLL_NUMBER> <PASSWORD>`.

The bot then displays the interactive main menu.

### Passwords with Spaces

If your Samvidha password contains one or more spaces, wrap the entire password in double quotes (`"..."`) or single quotes (`'...'`):

**Examples:**
```text
/login 21951A0501 "my secret password"
```
```text
/login 21951A0501 'my secret password'
```

---

## Main Menu Navigation

Once logged in, an interactive menu is displayed with the following options:

```text
+---------------------------+
|         MAIN MENU         |
+-------------+-------------+
| Attendance  | Bunk        |
+-------------+-------------+
| Biometric   | Logout      |
+-------------+-------------+
| Labs Records              |
+---------------------------+
| Student Info              |
+---------------------------+
| Saved Username            |
+---------------------------+
```

### Attendance
- **Function:** Displays your enrolled subjects for the current semester.
- **Data Provided:**
  - Subject code and course title.
  - Number of classes conducted versus attended.
  - Individual subject percentages.
  - Overall aggregate attendance percentage.

### Bunk Calculator
- **Function:** Calculates your attendance margin based on your target threshold (default: 75%, configurable under `/settings`).
- **Scenarios:**
  - **Attendance above threshold:** Indicates the exact number of classes you can miss while maintaining your target percentage.
  - **Attendance below threshold:** Calculates the number of consecutive future classes you must attend to return to the target threshold.

### Biometric Log
- **Function:** Tracks your campus presence for the current day.
- **Data Provided:**
  - First check-in timestamp.
  - Most recent check-out timestamp.
  - Total elapsed duration on campus.
  - Indication of whether the daily minimum hours requirement has been satisfied.

### PAT Attendance
- **Function:** Displays dedicated attendance metrics for Placement and Training (PAT) modules and campus recruitment training sessions.

### Lab Records
- **Function:** View, manage, and upload experiment records for laboratory courses.
- **Uploading Records:**
  1. Send your experiment PDF file directly to the bot in the private chat.
  2. Provide the experiment title when prompted (or let the bot detect it automatically if Auto-Extract is enabled in settings).
  3. **Automatic Compression:** If your document exceeds 1 MB, the bot automatically optimizes and compresses the file before submission to adhere to portal size restrictions.
- **Managing Records:**
  - Select any previously submitted record to view details or remove it if you wish to upload an updated version.

### Student Info
- **Function:** Summarizes comprehensive student academic records.
- **Available Sections:**
  - **Profile:** Full name, department, section, roll number, and assigned faculty mentor.
  - **Grades:** Semester-by-semester SGPA breakdown and overall cumulative CGPA.
  - **CIE Marks:** Continuous Internal Evaluation (mid-term examination) scores for current courses.
  - **Fee Payments:** Fee payment receipts, transaction references, and remaining balances.

### Saved Username
- **Function:** Displays the saved roll number associated with your chat.
- **Controls:**
  - **Remove:** Permanently deletes your saved credentials from the bot database.
  - **Remove and Logout:** Permanently deletes your saved credentials and terminates your active session.
  - **Back:** Returns to the main menu.
- **Tip for Checking a Friend's Account:** If you want to temporarily check a friend's records, do not click "Remove" or "Remove and Logout". Simply use the standard **Logout** button, log in using your friend's credentials, and click **"No"** when asked to save. When you log out of your friend's session, pressing any action button will automatically restore your own account!

### Logging Out
- **Function:** Ends your active session.
- **Usage:** Tap the **Logout** button on the menu or send:
  ```text
  /logout
  ```

---

## User Settings

Send `/settings` to open the configuration panel:

| Setting | Options | Description |
| :--- | :--- | :--- |
| **Attendance Threshold** | 65%, 70%, 75%, 80%, 85% | Sets the baseline percentage used by the Bunk Calculator. |
| **Biometric Threshold** | Configurable hours | Adjusts your daily campus stay duration goal. |
| **Title Extract** | Auto / Manual | Selects whether lab PDF titles are extracted automatically from the document or entered manually. |
| **User Interface** | Traditional / Updated | Toggles between compact monospace format and structured card layout. |

---

## Help and Issue Reporting

If you encounter an issue (e.g., incorrect attendance figures, upload errors) or have a feature suggestion, submit a ticket directly to the student maintainers:

```text
/report <description of your issue or request>
```

**Example:**
```text
/report My biometric out-time for today is not reflecting in the log.
```

- Every report is recorded with an exact timestamp in Indian Standard Time (IST).
- When a maintainer reviews and resolves your ticket, you will receive a direct notification in Telegram containing their response and resolution time.

---

## Frequently Asked Questions

**Q: Do I need to log in every day?**  
A: It depends on whether you saved your credentials:
- **If you clicked "Yes" to save your credentials:** No. Whenever your session expires, the bot will automatically re-log you in in the background as soon as you press any button (Attendance, Bunk, Biometric, etc.). You do not need to click anything to re-login.
- **If you clicked "No" (or did not save credentials):** Yes. Your login details were not stored, so you must log in again using `/login <ROLL_NUMBER> <PASSWORD>` whenever your session expires.

**Q: Why did my login attempt fail?**  
A: Common causes include:
- A typo in your roll number or password.
- A password containing spaces that was not wrapped in quotes (e.g., use `/login 21951A0501 "pass with space"`).
- Temporary downtime or maintenance on the Samvidha college server.

**Q: How do I change my target bunk percentage?**  
A: Send `/settings`, select **Attendance Threshold**, and pick your preferred percentage. The Bunk Calculator will immediately update its calculations based on this selection.

**Q: How do I delete my saved credentials from the bot?**  
A: Tap **Saved Username** on the main menu, select your roll number, and choose **Remove** (or **Remove and Logout**). Your credentials will be removed immediately.

**Q: Can I check a friend's account without losing my saved login?**  
A: Yes. Use this trick:
1. Tap the standard **Logout** button on the main menu (do not select "Remove" or "Remove and Logout").
2. Use `/login <FRIEND_ROLL> <FRIEND_PASSWORD>` to log into your friend's account.
3. When prompted to save credentials, select **"No"**.
4. Check your friend's attendance, marks, or records as needed.
5. Once done, tap **Logout** again. Because your original credentials were never deleted, pressing any menu button (like Attendance or Bunk) will automatically restore your own account in the background!
