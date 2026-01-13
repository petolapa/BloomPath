# UE5 Guide: Real 3D Visuals & Shrinking

> **Prerequisites**: Stop Play Mode! (Press Esc)

---

## Part 1: Visual Growth (Spawning Meshes)

We will modify `Grow_Leaves` to spawn actual 3D shapes.

### Step 1: Open `Grow_Leaves` Function
Double-click `Grow_Leaves` in `BP_GrowerActor`.

### Step 2: Add "Add Static Mesh Component"
1.  Drag off the execution pin (white arrow) from `Print String` (or just delete Print String).
2.  Search: **Add Static Mesh Component**.
3.  This node spawns a 3D object attached to your actor.

### Step 3: Configure the Mesh
1.  On the **Add Static Mesh Component** node, looks for **Manual Attachment** -> **Relative Transform**.
    *   Right-click `Relative Transform` pin -> **Split Struct Pin**.
    *   Now you see Location, Rotation, Scale separately.
2.  **Set the Mesh**:
    *   Click the node. In **Details Panel** (right), find **Static Mesh**.
    *   Set it to `Shape_Sphere` (or any shape you like).
3.  **Set Scale (Priority)**:
    *   Drag the **Growth_Modifier** input pin -> connect to **Relative Transform Scale 3D**.
    *   *Note: This automatically sets X, Y, Z to the modifier value (e.g., 2.0 = Double Size).*

### Step 4: Add Tag (Crucial for Shrinking!)
1.  Drag off the **Return Value** (Blue pin) of the *Add Static Mesh Component* node.
2.  Search: **Set Component Tags**.
3.  Drag the pink **Target Branch ID** input -> connect to **Array Element** (you might need to drag off `Tags` pin and type `Make Array` first, or just connect directly depending on UE version).
    *   *Goal: The mesh now has a hidden sticky note saying "KAN-32".*

### Step 5: Random Location (Optional but recommended)
1.  Right-click empty space: **Random Float in Range** (Min: -100, Max: 100).
2.  Do this 3 times (for X, Y, Z).
3.  Right-click: **Make Vector**. Connect the random floats.
4.  Connect this Vector to **Relative Transform Location** on the spawn node.

---

## Part 2: Shrink Logic (Removing Meshes)

We will implement `Shrink_Leaves` to delete the mesh.

### Step 1: Open `Shrink_Leaves` Function
Same inputs as before (`Target_Branch_ID`).

### Step 2: Find the Mesh
1.  Right-click: **Get Components by Tag**.
    *   **Component Class**: Select `StaticMeshComponent`.
    *   **Tag**: Connect your pink `Target_Branch_ID` input here.
2.  Look at the **Return Value** (Array of components).

### Step 3: Destroy It
1.  Drag off **Return Value** -> **ForEachLoop**.
2.  Connect the execution pin (entry) to the Loop.
3.  Drag off **Array Element** (from the Loop) -> Search **Destroy Component**.
4.  Connect **Loop Body** -> **Destroy Component**.

**Logic in English**: *"Find all meshes tagged 'KAN-32'. For each one found, destroy it."*

---

## Part 3: Compile, Save, Play!

1.  **Compile** & **Save**.
2.  **Play** the game.
3.  Move Jira Card to Done -> **See Sphere appear!**
4.  Move Jira Card back to In Progress -> **See Sphere vanish!**
5.  Check logs for errors.
