# Demo Mode UI Hardening

## Overview
A secure **Demo Mode** has been implemented on the frontend to ensure safe, controlled presentations. This mode dynamically hides sensitive features and settings without affecting the underlying permissions structure.

## Technical Implementation
1. **DemoContext**: A global React Context (`DemoContext.jsx`) has been introduced to manage the `isDemoMode` state. This state is persisted in `localStorage` (`gurukul_demo_mode`).
2. **Global Toggle**: A non-obtrusive "DEMO MODE" toggle has been added to the main Global `Navbar`. This toggle is only visible to authenticated users.

## Hardened UI Elements (Hidden During Demo Mode)
When Demo Mode is activated, the following UI elements are conditionally removed from the DOM to prevent accidental clicks during a live demo:

* **Admin Dashboard:**
  * `User Management` panel link
  * `System Overview` panel link
  * `Settings` gear icon and link
* **Teacher Dashboard:**
  * `Settings` gear icon and link

## Account Guarding
To prevent confusion between demo and production workflows, a safety guard has been added to the **Sign In** process:
* **Constraint:** Any account ending in `@demo.com` is strictly blocked from logging in unless **DEMO MODE** is active.
* **User Feedback:** If a user attempts to log in with a demo account while the mode is OFF, they receive a clear instruction to enable the toggle in the navigation bar.

*Note: The regular Student Sidebar does not contain sensitive internal panels by default, so its structure remains largely unchanged, preserving the authentic student flow.*
