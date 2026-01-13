# UE5 Blueprint Update Guide - Advanced Features

> **Prerequisites**: You have `BP_GrowerActor` with `Grow_Leaves` function from the initial setup.

---

## Part 1: Update `Grow_Leaves` Function

### Step 1: Open the Blueprint
1. In **Content Browser**, double-click `BP_GrowerActor`
2. In **My Blueprint** panel (left), click on `Grow_Leaves`

### Step 2: Add New Input Parameters
1. Look at the **Details** panel (right side)
2. Find **Inputs** section
3. Click **+** to add each new input:

| Name | Type |
|------|------|
| `Color_R` | Float |
| `Color_G` | Float |
| `Color_B` | Float |
| `Epic_ID` | String |

### Step 3: Use the Color (Optional Visual)
1. Double-click `Grow_Leaves` to open its graph
2. Right-click → search **Make Linear Color**
3. Connect `Color_R`, `Color_G`, `Color_B` pins to R, G, B inputs
4. Use output to set material color (for later)

### Step 4: Compile & Save
- Click **Compile** (blue checkmark)
- Click **Save** (Ctrl+S)

---

## Part 2: Create `Add_Thorns` Function

### Step 1: Add New Function
1. In **My Blueprint** panel, under **Functions**, click **+**
2. Name it: `Add_Thorns`

### Step 2: Add Inputs
In **Details** panel, add:

| Name | Type |
|------|------|
| `Target_Branch_ID` | String |
| `Epic_ID` | String |

### Step 3: Add Logic
1. Double-click `Add_Thorns` to open graph
2. Right-click → **Print String**
3. Connect execution from entry to Print String
4. Type: `🌵 Blocker detected!`

### Step 4: Enable Remote Control
1. Select `Add_Thorns` in My Blueprint panel
2. In Details, check ✅ **Call In Editor**

### Step 5: Compile & Save

---

## Part 3: Create `Remove_Thorns` Function (Optional)

Same steps as Add_Thorns:
1. Create function: `Remove_Thorns`
2. Add input: `Target_Branch_ID` (String)
3. Add Print String: `✅ Blocker resolved!`
4. Enable **Call In Editor**
5. Compile & Save

---

## Part 4: Test the New Functions

### Test via PowerShell
```powershell
# Test Grow_Leaves with color
$body = @{
    objectPath = "/Temp/Untitled_1.Untitled_1:PersistentLevel.BP_GrowerActor_C_UAID_E89C257B5B95F2B402_1503215167"
    functionName = "Grow_Leaves"
    parameters = @{
        Target_Branch_ID = "TEST-001"
        Growth_Type = "leaf"
        Growth_Modifier = 1.5
        Color_R = 1.0
        Color_G = 0.2
        Color_B = 0.2
        Epic_ID = "EPIC-1"
    }
} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8080/remote/object/call" -Method PUT -Body $body -ContentType "application/json"

# Test Add_Thorns
$body = @{
    objectPath = "/Temp/Untitled_1.Untitled_1:PersistentLevel.BP_GrowerActor_C_UAID_E89C257B5B95F2B402_1503215167"
    functionName = "Add_Thorns"
    parameters = @{
        Target_Branch_ID = "BLOCKED-001"
        Epic_ID = "EPIC-1"
    }
} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8080/remote/object/call" -Method PUT -Body $body -ContentType "application/json"
```

Check UE5 Output Log for the print messages!
