# 🎮 UE5 Beginner Guide for BloomPath

> **For**: First-time UE5 users | **Version**: UE 5.7.1

---

## Step 1: Launch Unreal Engine & Create Project

### 1.1 Open Epic Games Launcher
1. Open the **Epic Games Launcher**
2. Click **Unreal Engine** in the left sidebar
3. Click the **Launch** button next to version **5.7.1**

### 1.2 Create a New Project
1. In the **Unreal Project Browser**, select **Games** → **Blank**
2. Configure:
   | Setting | Value |
   |---------|-------|
   | Project Name | `BloomPath_Garden` |
   | Location | Choose your preferred folder |
   | Blueprint | ✅ Selected (not C++) |
3. Click **Create**

> ⏱️ Wait for the editor to load (may take 1-2 minutes first time)

---

## Step 2: Enable Remote Control Plugin

This lets BloomPath send commands to UE5.

### 2.1 Open Plugin Settings
1. Click **Edit** menu (top bar)
2. Select **Plugins**

### 2.2 Find & Enable Plugin
1. In the search box, type: `Remote Control`
2. Find **"Remote Control API"**
3. Check the ✅ **Enabled** checkbox
4. Click **Restart Now** when prompted

---

## Step 3: Configure Remote Control Settings

### 3.1 Open Project Settings
1. Click **Edit** → **Project Settings**
2. In the left panel, scroll down and click **Plugins** → **Remote Control**

### 3.2 Set These Values
| Setting | Value |
|---------|-------|
| Enable Remote Control | ✅ Checked |
| HTTP Server Port | `8080` |
| Enable HTTP Server | ✅ Checked |

3. Close Project Settings (changes auto-save)

---

## Step 4: Create the GrowerActor Blueprint

### 4.1 Open Content Browser
1. Look at the bottom of the screen for the **Content Browser** panel
2. If not visible: click **Window** → **Content Browser** → **Content Browser 1**

### 4.2 Create New Blueprint
1. **Right-click** in the empty Content Browser area
2. Select **Blueprint Class**
3. In the popup, click **Actor**
4. Name it: `BP_GrowerActor`
5. **Double-click** to open the Blueprint Editor

---

## Step 5: Add Components to Blueprint

### 5.1 Add Components Panel
In the Blueprint Editor, look at the left side for **Components** panel.

### 5.2 Add These Components
1. Click **+ Add** button
2. Search and add: **Static Mesh** → name it `TreeMesh`
3. Click **+ Add** again
4. Search and add: **Static Mesh** → name it `LeavesMesh`

### 5.3 Set a Basic Mesh (Optional Visual)
1. Select `TreeMesh` in the Components panel
2. In the **Details** panel (right side), find **Static Mesh**
3. Click the dropdown → search for `Cube` or any mesh
4. Do the same for `LeavesMesh`

---

## Step 6: Create the Grow_Leaves Function

### 6.1 Open Functions Panel
1. In the Blueprint Editor, look at the left side for **My Blueprint** panel
2. Under **Functions**, click the **+** button
3. Name the new function: `Grow_Leaves`

### 6.2 Add Input Parameter
1. Select the `Grow_Leaves` function
2. In the **Details** panel (right side), find **Inputs**
3. Click **+** to add a new input
4. Set:
   | Property | Value |
   |----------|-------|
   | Name | `Target_Branch_ID` |
   | Type | `String` |

### 6.3 Add Simple Logic
1. Double-click `Grow_Leaves` to open its graph
2. **Right-click** in the empty area → search for **Print String**
3. Connect the execution pin (white arrow) from the function entry to Print String
4. In the Print String node, type: `Growth triggered!`

Your function graph should look like:
```
[Grow_Leaves] ──► [Print String: "Growth triggered!"]
```

---

## Step 7: Expose Function to Remote Control

### 7.1 Enable Call in Editor
1. Select the `Grow_Leaves` function in My Blueprint panel
2. In **Details** panel, find **Graph** section
3. Check ✅ **Call In Editor**

### 7.2 Compile and Save
1. Click the **Compile** button (top toolbar, blue checkmark icon)
2. Click **Save** (Ctrl+S)

---

## Step 8: Place Actor in Your Level

### 8.1 Drag to Level
1. Close the Blueprint Editor (or keep it open)
2. In Content Browser, find `BP_GrowerActor`
3. **Drag and drop** it into the main viewport (center of screen)

### 8.2 Get Actor Path for Config
1. Click on the placed actor in the viewport
2. Look at the **World Outliner** panel (usually top-right)
3. Right-click the actor → **Copy Reference**
4. Save this path - you'll need it for the `.env` file

Example path:
```
/Game/MainLevel.MainLevel:PersistentLevel.BP_GrowerActor_C_0
```

---

## Step 9: Test the Setup

### 9.1 Start Play in Editor (PIE)
1. Click the **▶️ Play** button in the main toolbar
2. The game will start in the viewport

### 9.2 Test Remote Control API
Open **PowerShell** and run:

```powershell
Invoke-RestMethod -Uri "http://localhost:8080/remote/info"
```

You should see Remote Control API information returned.

### 9.3 Test Grow_Leaves Function
```powershell
$body = @{
    objectPath = "/Game/MainLevel.MainLevel:PersistentLevel.BP_GrowerActor_C_0"
    functionName = "Grow_Leaves"
    parameters = @{
        Target_Branch_ID = "TEST-001"
    }
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8080/remote/object/call" -Method PUT -Body $body -ContentType "application/json"
```

Check the UE5 output log for "Growth triggered!"

---

## Step 10: Update BloomPath Config

Update your `.env` file with the actor path:

```
UE5_ACTOR_PATH=/Game/MainLevel.MainLevel:PersistentLevel.BP_GrowerActor_C_0
```

Then restart the Docker container:
```powershell
docker compose down
docker compose up -d
```

---

## Quick Reference

| Keyboard Shortcut | Action |
|-------------------|--------|
| **F** | Focus on selected object |
| **W, E, R** | Move, Rotate, Scale tools |
| **Ctrl+S** | Save |
| **Alt+P** | Play in Editor |
| **Esc** | Stop Play |

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Can't find Remote Control plugin | Ensure you're on UE 5.0+ |
| Connection refused on 8080 | Make sure PIE is running |
| Function not found | Check "Call In Editor" is enabled |
| No output log | Open View → Output Log |
