# Tempered Windows: Windows System Hardening GUI Application

## 1. Project Overview

### 1.1 Project Title
Tempered Windows

### 1.2 Project Description
Tempered Windows is a graphical user interface (GUI) application designed to make Windows system hardening accessible, safe, and reversible.  
The name "Tempered" subtly reflects the process of strengthening and refining the operating system — like tempering steel to make it tougher yet still flexible and reliable.

Users can load predefined hardening rule sets from external files, organized into logical categories. Through an intuitive checkbox interface, they select which categories to apply. When ready, a single "Apply" button triggers the hardening process, using Microsoft’s LGPO tool (preferred for policy-based settings) or direct Registry modifications when needed.

To ensure safety and trust, the application automatically creates detailed backups of all modified values before making any changes. A dedicated "Revert" feature then allows users to either restore the original (pre-hardening) values or fall back to Microsoft’s recommended defaults — giving full control and peace of mind.

Built in **Python 3.13**, Tempered Windows targets modern Windows environments (Windows 10 & 11) and aims to be lightweight, user-friendly, and community-extensible through simple JSON rule files.

### 1.3 Objectives
- Deliver a clean, modern GUI for selecting and applying hardening configurations
- Support modular, file-based rule sets that are easy to share and extend
- Group rules into meaningful categories with clear checkbox controls
- Prefer LGPO for policy-level changes; fall back gracefully to Registry edits
- Always back up original values before modification
- Provide flexible, per-category or per-rule reversion (original vs default)
- Require and handle elevated privileges correctly and transparently
- Keep the application portable and dependency-light

### 1.4 Scope
**In Scope**  
- GUI for rule selection & application  
- JSON-based rule loading/saving  
- Automatic backup & revert functionality  
- LGPO + Registry application methods  
- Basic logging and user-friendly error messages  

**Out of Scope** (for initial versions)  
- Real-time compliance auditing  
- Automatic rule updates from the internet  
- Multi-system / domain-wide deployment  
- Non-Windows operating systems  

### 1.5 Target Audience
- Security-conscious Windows users  
- IT administrators and consultants  
- Enthusiasts and power users who want better control over system security  
- People who value reversibility and transparency when hardening their systems  

### 1.6 Assumptions and Constraints
- Application runs on Windows only  
- Requires Python 3.13 (or packaged executable)  
- LGPO.exe should be present (Microsoft Security Compliance Toolkit) or the app falls back to Registry  
- User must have administrative rights (UAC elevation handled automatically)  
- Rule files use JSON format for simplicity and readability  
