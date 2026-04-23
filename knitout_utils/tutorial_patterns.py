"""
Tutorial Pattern Generator
===========================
Generates six knitout patterns using the KnittingHelper and ShapingHelper classes.

Patterns:
  1. basic_tube        - Plain tubular knitting
  2. branching_tube    - One tube splitting into two
  3. widening_tube     - Tube that grows wider via increases
  4. half_bodice       - Flat half-bodice panel with waist/bust shaping
  5. blister_bubble    - Tubular blister stitch (short-row 3D bubbles)
  6. bulges            - Tube with localized bulge (increase then decrease)

Usage:
    python tutorial_patterns.py
    # Generates: basic_tube.k, branching_tube.k, widening_tube.k,
    #            half_bodice.k, blister_bubble.k, bulges.k
"""

from shaping_helper import ShapingHelper


# =====================================================================
# 1. Basic Tube
# =====================================================================

def basic_tube(width=20, body_rows=40, filename="basic_tube.k"):
    """
    A plain half-gauge tube.

    Steps:
      - All-needle-transition cast-on
      - Knit `body_rows` tubular rows
      - Chain bind-off

    Parameters:
        width:      number of logical stitches around the tube
        body_rows:  how many tubular rows to knit
        filename:   output knitout filename
    """
    sh = ShapingHelper(width=width, is_tubular=True)
    sh.standard_headers()

    carrier = 3
    sh.cast_on_all_needle_transition(carrier, settling_rows=4)

    for _ in range(body_rows):
        sh.knit_tubular_row(carrier)

    sh.bind_off_tubular(carrier)

    output = sh.write(filename)
    print(f"[basic_tube] Generated {len(output.splitlines())} lines -> {filename}")


# =====================================================================
# 2. Branching Tube (one tube splits into two)
# =====================================================================

def _knit_sub_tube_row(sh, carrier, lo, hi):
    """
    Knit one tubular row on a sub-range [lo, hi] of logical needles.
    Uses the same half-gauge addressing as ShapingHelper._loc().

    The carrier direction is tracked via sh.direction[carrier].
    """
    if sh.direction[carrier] == "-":
        # Front bed: right to left
        for n in range(hi, lo - 1, -1):
            sh.knit("-", f"f{2 * n}", carrier)
        # Back bed: left to right
        for n in range(lo, hi + 1):
            sh.knit("+", f"b{2 * n + 1}", carrier)
    else:
        # Front bed: left to right
        for n in range(lo, hi + 1):
            sh.knit("+", f"f{2 * n}", carrier)
        # Back bed: right to left
        for n in range(hi, lo - 1, -1):
            sh.knit("-", f"b{2 * n + 1}", carrier)


def _drop_sub_tube(sh, carrier, lo, hi):
    """Drop all loops for a sub-range and outhook the carrier."""
    sh.outhook(carrier)
    for n in range(lo, hi + 1):
        sh.drop(f"f{2 * n}")
        sh.drop(f"b{2 * n + 1}")


def branching_tube(width=20, trunk_rows=30, branch_rows=25,
                   filename="branching_tube.k"):
    """
    A tube that splits into two tubes at a branch point.

    Strategy:
      - Cast on a single tube of `width` stitches using carrier 3.
      - Knit the trunk for `trunk_rows`.
      - At the branch point, bring in carrier 4 for the right branch.
        Carrier 3 continues knitting the left branch.
      - Each branch is half the original width.
      - Drop all stitches at the end (quick teardown for testing).

    The branch is created by restricting each carrier to its own
    sub-range of needles, effectively splitting the tube in two.
    A few "bridge" tucks at the split boundary keep the yarn stable
    during the transition.

    Parameters:
        width:        stitches in the main tube (must be even)
        trunk_rows:   rows before the split
        branch_rows:  rows for each branch after the split
        filename:     output knitout filename
    """
    assert width % 2 == 0, "width must be even for a clean split"
    assert width >= 8, "need at least 8 stitches for branching"

    sh = ShapingHelper(width=width, is_tubular=True)
    sh.standard_headers()

    main_carrier = 3
    branch_carrier = 4

    # --- Trunk ---
    sh.cast_on_all_needle_transition(main_carrier, settling_rows=4)
    for _ in range(trunk_rows):
        sh.knit_tubular_row(main_carrier)

    # --- Branch point ---
    # Left half: logical needles [min_n, mid]
    # Right half: logical needles [mid+1, max_n]
    mid = sh.min_n + (width // 2) - 1

    left_lo, left_hi = sh.min_n, mid
    right_lo, right_hi = mid + 1, sh.max_n

    # Bring in the branch carrier with tucks on the right sub-tube
    sh.inhook(branch_carrier)
    # Tuck across right-half front needles to anchor
    for n in range(right_hi, right_lo - 1, -1):
        sh.tuck("-", f"f{2 * n}", branch_carrier)
    for n in range(right_lo, right_hi + 1):
        sh.tuck("+", f"b{2 * n + 1}", branch_carrier)
    sh.releasehook(branch_carrier)
    sh.direction[branch_carrier] = "-"

    # --- Knit branches alternately ---
    # We alternate: a few rows on the left, a few rows on the right.
    # This keeps both carriers active and avoids very long floats.
    chunk = 5  # rows per alternation
    for i in range(0, branch_rows, chunk):
        rows_this_chunk = min(chunk, branch_rows - i)
        # Left branch (carrier 3)
        for _ in range(rows_this_chunk):
            _knit_sub_tube_row(sh, main_carrier, left_lo, left_hi)
        # Right branch (carrier 4)
        for _ in range(rows_this_chunk):
            _knit_sub_tube_row(sh, branch_carrier, right_lo, right_hi)

    # --- Teardown ---
    _drop_sub_tube(sh, main_carrier, left_lo, left_hi)
    _drop_sub_tube(sh, branch_carrier, right_lo, right_hi)

    output = sh.write(filename)
    print(f"[branching_tube] Generated {len(output.splitlines())} lines -> {filename}")


# =====================================================================
# 3. Widening Tube
# =====================================================================

def widening_tube(start_width=10, increases=6, rows_between=6,
                  tail_rows=20, filename="widening_tube.k"):
    """
    A tube that gradually grows wider through periodic increases.

    Steps:
      - Cast on at `start_width`.
      - Alternate: increase by 1 stitch on the right, knit settling
        rows, increase by 1 on the left, knit settling rows.
      - After all increases, knit `tail_rows` at the final width.
      - Drop all (quick teardown).

    Parameters:
        start_width:   initial tube width
        increases:     total number of increase operations
        rows_between:  settling rows between each increase
        tail_rows:     rows to knit after all increases
        filename:      output knitout filename
    """
    sh = ShapingHelper(width=start_width, is_tubular=True)
    sh.standard_headers()

    carrier = 3
    sh.cast_on_all_needle_transition(carrier, settling_rows=4)

    # Knit some initial rows
    for _ in range(10):
        sh.knit_tubular_row(carrier)

    # Alternate right-lean and left-lean increases
    for i in range(increases):
        if i % 2 == 0:
            # Right-lean increase: grow max_n side
            pos = sh.max_n
            sh.increase(positions=pos, carrier=carrier, lean="right")
        else:
            # Left-lean increase: grow min_n side
            pos = sh.min_n
            sh.increase(positions=pos, carrier=carrier, lean="left")

        # Settling rows
        for _ in range(rows_between):
            sh.knit_tubular_row(carrier)

        print(f"  [widening_tube] After increase #{i+1}: "
              f"width={sh.width} [{sh.min_n}, {sh.max_n}]")

    # Tail section at final width
    for _ in range(tail_rows):
        sh.knit_tubular_row(carrier)

    sh.drop_all_tubular(carrier)

    output = sh.write(filename)
    print(f"[widening_tube] Generated {len(output.splitlines())} lines -> {filename}")


# =====================================================================
# 4. Half Bodice (flat piece)
# =====================================================================

def half_bodice(hip_width=30, waist_decreases=4, bust_increases=3,
                armhole_decreases=3, section_rows=8,
                filename="half_bodice.k"):
    """
    A flat half-bodice panel with shaping:
      - Hip section (straight)
      - Waist shaping (decreases on both sides)
      - Bust shaping (increases on the right / bust side)
      - Upper bodice (straight)
      - Armhole (decreases on the right side)
      - Shoulder (straight, then bind off)

    This is a flat (non-tubular) piece on the front bed.

    Parameters:
        hip_width:          starting width at the hip
        waist_decreases:    number of decrease ops for waist shaping
        bust_increases:     number of increase ops for bust
        armhole_decreases:  number of decrease ops for armhole
        section_rows:       rows between each shaping operation
        filename:           output knitout filename
    """
    sh = ShapingHelper(width=hip_width, is_tubular=False)
    sh.standard_headers()

    carrier = 1

    # --- Cast on + hip section ---
    sh.cast_on_flat(carrier)
    for _ in range(section_rows * 2):
        sh.knit_flat_row(carrier)

    print(f"  [bodice] Hip: width={sh.width} [{sh.min_n}, {sh.max_n}]")

    # --- Waist shaping: decrease both sides ---
    for i in range(waist_decreases):
        # Left decrease (shifts left edge right)
        sh.decrease(position=sh.min_n + 2, lean="left")
        for _ in range(2):
            sh.knit_flat_row(carrier)
        # Right decrease (shifts right edge left)
        sh.decrease(position=sh.max_n - 2, lean="right")
        for _ in range(section_rows - 2):
            sh.knit_flat_row(carrier)
        print(f"  [bodice] Waist dec #{i+1}: width={sh.width} "
              f"[{sh.min_n}, {sh.max_n}]")

    # Knit a few straight rows at the waist
    for _ in range(section_rows):
        sh.knit_flat_row(carrier)

    # --- Bust shaping: increase on the right side ---
    # increase() requires direction "-", and it knits a row internally,
    # so we need direction to be "-" on entry. After an even number of
    # flat rows, direction alternates. Let's ensure it's "-".
    if sh.direction[carrier] != "-":
        sh.knit_flat_row(carrier)  # extra row to get to "-"

    for i in range(bust_increases):
        sh.increase(positions=sh.max_n, carrier=carrier, lean="right")
        sh.knit_flat_row(carrier)  # settling row ("+" -> "-")
        # Additional rows between increases
        for _ in range(section_rows - 2):
            sh.knit_flat_row(carrier)
        # Ensure direction is "-" for next increase
        if sh.direction[carrier] != "-":
            sh.knit_flat_row(carrier)
        print(f"  [bodice] Bust inc #{i+1}: width={sh.width} "
              f"[{sh.min_n}, {sh.max_n}]")

    # --- Upper bodice (straight) ---
    for _ in range(section_rows * 2):
        sh.knit_flat_row(carrier)

    # --- Armhole shaping: decrease on the right side ---
    for i in range(armhole_decreases):
        sh.decrease(position=sh.max_n - 2, lean="right")
        for _ in range(section_rows):
            sh.knit_flat_row(carrier)
        print(f"  [bodice] Armhole dec #{i+1}: width={sh.width} "
              f"[{sh.min_n}, {sh.max_n}]")

    # --- Shoulder (straight) + bind off ---
    for _ in range(section_rows):
        sh.knit_flat_row(carrier)

    sh.bind_off_flat(carrier)

    output = sh.write(filename)
    print(f"[half_bodice] Generated {len(output.splitlines())} lines -> {filename}")


# =====================================================================
# 5. Blister / Bubble Pattern
# =====================================================================

def blister_bubble(width=20, num_repeats=3, body_rows=6,
                   filename="blister_bubble.k"):
    """
    Tubular blister stitch using short rows to create 3D bubbles.

    The blister is created by knitting short rows on the tube: the
    center needles receive more rows than the edges, causing the
    center fabric to puff outward into a dome-shaped bubble.

    One repeat (matching the uploaded screenshot pattern):
      - Knit `body_rows` plain tubular rows (flat band)
      - Do a series of short-row turns that progressively narrow
        from the full width down to a small center section, then
        widen back out. This creates a staircase of fabric heights
        that puckers into a 3D blister.

    The short-row turns are placed on the back bed, progressing
    inward from both edges toward the center, then back out.

    Parameters:
        width:        tube width
        num_repeats:  how many blister repeats
        body_rows:    plain rows between blisters
        filename:     output knitout filename
    """
    sh = ShapingHelper(width=width, is_tubular=True)
    sh.standard_headers()

    carrier = 3
    sh.cast_on_all_needle_transition(carrier, settling_rows=4)

    # Initial plain rows
    for _ in range(body_rows):
        sh.knit_tubular_row(carrier)

    for rep in range(num_repeats):
        # Build short-row turn points: narrow in from edges, creating
        # a pyramid of extra rows in the center.
        #
        # The turns form a staircase pattern like the screenshot:
        #   - Turn at 80% from left, then 20% from left (outer ring)
        #   - Turn at 65% from left, then 35% from left (middle ring)
        #   - Turn at max, then min+1 (widest pass)
        #   - Turn at 65%, then 35% on front bed (closing passes)
        #
        # This matches the J-30 style short rows in the shaping helper.
        turns = []
        steps = max(3, width // 5)  # number of narrowing steps
        for s in range(steps):
            frac = 0.15 + s * (0.35 / steps)
            n_right = round((1.0 - frac) * (sh.max_n - sh.min_n) + sh.min_n)
            n_left = round(frac * (sh.max_n - sh.min_n) + sh.min_n)
            # Clamp to valid range
            n_right = min(n_right, sh.max_n)
            n_left = max(n_left, sh.min_n + 1)
            turns.append({"b": "b", "n": n_right})
            turns.append({"b": "b", "n": n_left})

        # Add widest pass and front-bed closing turns
        turns.append({"b": "b", "n": sh.max_n})
        turns.append({"b": "b", "n": sh.min_n + 1})
        turns.append({"b": "f", "n": round(0.65 * (sh.max_n - sh.min_n) + sh.min_n)})
        turns.append({"b": "f", "n": round(0.35 * (sh.max_n - sh.min_n) + sh.min_n)})

        sh.short_rows(turns, carrier)

        # Plain rows between repeats
        for _ in range(body_rows):
            sh.knit_tubular_row(carrier)

        print(f"  [blister] Repeat #{rep+1} done")

    sh.drop_all_tubular(carrier)

    output = sh.write(filename)
    print(f"[blister_bubble] Generated {len(output.splitlines())} lines -> {filename}")


# =====================================================================
# 6. Bulges (tube with localized widening)
# =====================================================================

def bulges(width=16, num_bulges=2, increase_steps=4,
           rows_between_shaping=4, rows_between_bulges=10,
           filename="bulges.k"):
    """
    A tube with localized barrel-shaped bulges: the tube widens
    through increases, holds at the wider width, then narrows back
    through decreases.

    Matches the uploaded screenshot showing a rounded hexagonal
    profile (wider in the middle, tapering at top and bottom).

    Each bulge:
      - Increase both sides `increase_steps` times
        (alternating right-lean and left-lean increases with
         settling rows in between)
      - Knit at the widest width for a section
      - Decrease both sides `increase_steps` times to return
        to the original width

    Parameters:
        width:                  base tube width
        num_bulges:             number of bulge repeats
        increase_steps:         increases per side per bulge
        rows_between_shaping:   settling rows between each inc/dec
        rows_between_bulges:    plain rows between bulge repeats
        filename:               output knitout filename
    """
    sh = ShapingHelper(width=width, is_tubular=True)
    sh.standard_headers()

    carrier = 3
    sh.cast_on_all_needle_transition(carrier, settling_rows=4)

    # Initial section
    for _ in range(rows_between_bulges):
        sh.knit_tubular_row(carrier)

    for bulge in range(num_bulges):
        original_min = sh.min_n
        original_max = sh.max_n

        # --- Widening phase: increase both sides ---
        for i in range(increase_steps):
            # Right-lean increase (grows max_n)
            sh.increase(positions=sh.max_n, carrier=carrier, lean="right")
            for _ in range(rows_between_shaping):
                sh.knit_tubular_row(carrier)

            # Left-lean increase (grows min_n)
            sh.increase(positions=sh.min_n, carrier=carrier, lean="left")
            for _ in range(rows_between_shaping):
                sh.knit_tubular_row(carrier)

            print(f"  [bulges] Bulge #{bulge+1}, inc #{i+1}: "
                  f"width={sh.width} [{sh.min_n}, {sh.max_n}]")

        # --- Hold at widest width ---
        for _ in range(rows_between_bulges):
            sh.knit_tubular_row(carrier)

        # --- Narrowing phase: decrease both sides ---
        for i in range(increase_steps):
            # Decrease left side
            sh.decrease(position=sh.min_n + 2, lean="left")
            sh.knit_tubular_row(carrier)
            for _ in range(rows_between_shaping - 1):
                sh.knit_tubular_row(carrier)

            # Decrease right side
            sh.decrease(position=sh.max_n - 2, lean="right")
            sh.knit_tubular_row(carrier)
            for _ in range(rows_between_shaping - 1):
                sh.knit_tubular_row(carrier)

            print(f"  [bulges] Bulge #{bulge+1}, dec #{i+1}: "
                  f"width={sh.width} [{sh.min_n}, {sh.max_n}]")

        # Plain rows between bulges
        for _ in range(rows_between_bulges):
            sh.knit_tubular_row(carrier)

    sh.drop_all_tubular(carrier)

    output = sh.write(filename)
    print(f"[bulges] Generated {len(output.splitlines())} lines -> {filename}")


# =====================================================================
# Main
# =====================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Tutorial Pattern Generator")
    print("=" * 60)

    print("\n--- 1. Basic Tube ---")
    basic_tube()

    print("\n--- 2. Branching Tube ---")
    branching_tube()

    print("\n--- 3. Widening Tube ---")
    widening_tube()

    print("\n--- 4. Half Bodice ---")
    half_bodice()

    print("\n--- 5. Blister / Bubble ---")
    blister_bubble()

    print("\n--- 6. Bulges ---")
    bulges()

    print("\n" + "=" * 60)
    print("All patterns generated successfully!")
    print("=" * 60)
