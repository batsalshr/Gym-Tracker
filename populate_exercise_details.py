"""Populate exercise descriptions and instructions."""
import os
import sys
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gym_tracker.settings')
import django
django.setup()

from workouts.models import Exercise

# Exercise data: name -> (description, [steps])
EXERCISE_DATA = {
    # CHEST
    'Barbell Bench Press': (
        'Main chest strength builder (also triceps/front delts).',
        [
            'Lie on bench, eyes under bar, feet flat.',
            'Grip bar slightly wider than shoulders.',
            'Unrack, bring bar over mid-chest.',
            'Lower to mid-chest (elbows ~45–75°).',
            'Press up to lockout, keep shoulder blades squeezed.'
        ]
    ),
    'Incline Barbell Bench Press': (
        'Upper chest emphasis bench press.',
        [
            'Set bench to 30-45 degree incline.',
            'Grip bar slightly wider than shoulders.',
            'Unrack, bring bar over upper chest.',
            'Lower to upper chest with control.',
            'Press up to lockout.'
        ]
    ),
    'Decline Barbell Bench Press': (
        'Lower chest emphasis bench press.',
        [
            'Set bench to decline position.',
            'Grip bar slightly wider than shoulders.',
            'Unrack, bring bar over lower chest.',
            'Lower to lower chest with control.',
            'Press up to lockout.'
        ]
    ),
    'Close-Grip Bench Press': (
        'Triceps-focused bench press variation.',
        [
            'Bench setup like regular bench press.',
            'Hands shoulder-width apart.',
            'Lower to chest with elbows closer to body.',
            'Press up focusing on triceps.',
            'Keep shoulder blades squeezed throughout.'
        ]
    ),
    'Dumbbell Bench Press': (
        'Chest press with more range and balance work.',
        [
            'Sit with dumbbells on thighs, lie back and kick them up.',
            'Set shoulder blades back and down.',
            'Lower DBs to chest line (wrists stacked over elbows).',
            'Press up and slightly inward.',
            'Control the weight throughout.'
        ]
    ),
    'Incline Dumbbell Bench Press': (
        'Upper chest dumbbell press.',
        [
            'Set bench to 30-45 degree incline.',
            'Press dumbbells from shoulders.',
            'Lower with control to chest level.',
            'Press up and slightly inward.',
            'Keep shoulder blades squeezed.'
        ]
    ),
    'Decline Dumbbell Bench Press': (
        'Lower chest dumbbell press.',
        [
            'Set bench to decline position.',
            'Press dumbbells from lower chest.',
            'Lower with control.',
            'Press up to lockout.',
            'Maintain stable shoulder position.'
        ]
    ),
    'Dumbbell Fly': (
        'Chest isolation with stretch and squeeze.',
        [
            'Lie on bench, DBs above chest, slight elbow bend.',
            'Open arms wide in an arc until chest stretch.',
            'Bring DBs back together like hugging a barrel.',
            'Keep elbows softly bent throughout.',
            'Focus on the chest squeeze at top.'
        ]
    ),
    'Incline Dumbbell Fly': (
        'Upper chest isolation fly.',
        [
            'Set bench to 30-45 degree incline.',
            'Start with DBs above upper chest.',
            'Open arms wide until stretch.',
            'Bring together with chest squeeze.',
            'Maintain slight elbow bend.'
        ]
    ),
    'Cable Crossover': (
        'Constant-tension chest isolation.',
        [
            'Set pulleys at desired height.',
            'Step forward with slight lean, chest up.',
            'Bring hands together in front of chest.',
            'Pause and squeeze at bottom.',
            'Return with control.'
        ]
    ),
    'Cable Fly': (
        'Cable chest fly with constant tension.',
        [
            'Set cables at chest height.',
            'Stand centered, slight forward lean.',
            'Bring hands together in arc motion.',
            'Squeeze chest at center.',
            'Return slowly to stretch.'
        ]
    ),
    'Pec Deck': (
        'Machine fly for strict chest isolation.',
        [
            'Set seat so handles align with mid-chest.',
            'Keep chest tall, shoulders back.',
            'Bring arms together, squeeze.',
            'Return slow to a stretch.',
            'Control throughout range of motion.'
        ]
    ),
    'Push-Up': (
        'Bodyweight chest press.',
        [
            'Hands under shoulders or slightly wider.',
            'Body straight from head to heels.',
            'Brace core, squeeze glutes.',
            'Lower chest toward floor.',
            'Push back up without hips sagging.'
        ]
    ),
    'Chest Dip': (
        'Deep chest and triceps press.',
        [
            'Grip bars, lockout at top.',
            'Lean forward slightly, legs back.',
            'Lower until you feel chest stretch.',
            'Don\'t shrug shoulders.',
            'Push up keeping elbows tracking back.'
        ]
    ),
    'Dip': (
        'Compound chest and triceps builder.',
        [
            'Grip parallel bars, arms straight.',
            'Lean forward for chest emphasis.',
            'Lower body with control.',
            'Go until upper arms parallel to floor.',
            'Press back up to lockout.'
        ]
    ),
    
    # BACK
    'Pull-Up': (
        'Best bodyweight lat builder.',
        [
            'Grip bar overhand, hang with shoulders down.',
            'Pull chest toward bar (elbows to ribs).',
            'Pause near top.',
            'Lower fully under control.',
            'Avoid swinging or kipping.'
        ]
    ),
    'Chin-Up': (
        'Underhand pull-up with more biceps.',
        [
            'Grip bar underhand (palms facing you).',
            'Hang with shoulders engaged.',
            'Pull chin over bar.',
            'Squeeze at top.',
            'Lower with control.'
        ]
    ),
    'Lat Pulldown': (
        'Pull-up substitute with adjustable load.',
        [
            'Sit with thighs locked, chest up.',
            'Pull bar to upper chest.',
            'Keep elbows down and back.',
            'Control up without shoulders shrugging.',
            'Full stretch at top.'
        ]
    ),
    'Close-Grip Lat Pulldown': (
        'Lat pulldown with close neutral grip.',
        [
            'Use close neutral grip handle.',
            'Sit tall, chest up.',
            'Pull handle to upper chest.',
            'Squeeze lats at bottom.',
            'Control back to full stretch.'
        ]
    ),
    'Barbell Row': (
        'Back thickness and lat builder.',
        [
            'Hinge at hips, back flat, bar below knees.',
            'Brace core, keep neck neutral.',
            'Row bar to lower ribs/upper stomach.',
            'Lower slow, keep torso angle stable.',
            'Don\'t use momentum.'
        ]
    ),
    'Bent Over Row': (
        'Classic back thickness exercise.',
        [
            'Hinge forward at hips, back flat.',
            'Grip bar just outside legs.',
            'Pull to lower chest/upper abs.',
            'Squeeze shoulder blades together.',
            'Lower with control.'
        ]
    ),
    'Pendlay Row': (
        'Dead-stop barbell row for power.',
        [
            'Bar starts on floor each rep.',
            'Hinge over, back parallel to floor.',
            'Explosively row to lower chest.',
            'Return bar to floor.',
            'Reset between each rep.'
        ]
    ),
    'One-Arm Dumbbell Row': (
        'Unilateral lat and mid-back builder.',
        [
            'Hand and knee on bench, back flat.',
            'Pull DB toward hip (not straight up).',
            'Squeeze lat at top.',
            'Don\'t twist torso.',
            'Lower to full stretch.'
        ]
    ),
    'Dumbbell Row': (
        'Single-arm back row.',
        [
            'Support with one hand on bench.',
            'Row dumbbell to hip.',
            'Keep elbow close to body.',
            'Squeeze back at top.',
            'Lower with control.'
        ]
    ),
    'Seated Cable Row': (
        'Mid-back and lats with constant tension.',
        [
            'Sit tall, slight knee bend, chest up.',
            'Pull handle to mid-torso.',
            'Squeeze shoulder blades together.',
            'Reach forward with control.',
            'Don\'t round lower back.'
        ]
    ),
    'Cable Row': (
        'Constant tension back row.',
        [
            'Sit or stand at cable station.',
            'Pull handle to torso.',
            'Squeeze back muscles.',
            'Control the return.',
            'Maintain upright posture.'
        ]
    ),
    'Face Pull': (
        'Rear delts, upper back, and shoulder health.',
        [
            'Rope at face height, thumbs toward you.',
            'Pull rope to nose/forehead.',
            'Elbows high, externally rotate at end.',
            'Squeeze rear delts.',
            'Return slow.'
        ]
    ),
    'T-Bar Row': (
        'Heavy back thickness builder.',
        [
            'Chest up, hinge slightly.',
            'Pull handle toward lower chest.',
            'Squeeze shoulder blades.',
            'Lower under control.',
            'Keep core braced.'
        ]
    ),
    'Dumbbell Shrug': (
        'Upper trap isolation.',
        [
            'Hold DBs at sides.',
            'Lift shoulders straight up.',
            'Pause at top.',
            'Lower slowly.',
            'Don\'t roll shoulders.'
        ]
    ),
    'Barbell Shrug': (
        'Heavy trap builder.',
        [
            'Hold bar at thighs.',
            'Shrug shoulders to ears.',
            'Hold at top briefly.',
            'Lower with control.',
            'Keep arms straight.'
        ]
    ),
    'Cable High Row': (
        'Upper-back emphasis row.',
        [
            'Handles at high position.',
            'Pull toward face/upper chest.',
            'Elbows wide.',
            'Control back.',
            'Squeeze upper back.'
        ]
    ),
    'Assisted Pull-Up': (
        'Pull-up progression tool.',
        [
            'Kneel or stand on platform.',
            'Grip bar.',
            'Pull chest up toward bar.',
            'Lower slow.',
            'Control the assistance.'
        ]
    ),
    'Inverted Row': (
        'Bodyweight horizontal pull.',
        [
            'Body straight under bar.',
            'Pull chest to bar.',
            'Pause at top.',
            'Lower controlled.',
            'Keep body rigid.'
        ]
    ),
    'Deadlift': (
        'Full posterior chain builder (back/hips/legs).',
        [
            'Feet mid-foot under bar, hip-width.',
            'Grip bar, bring shins to bar, chest up.',
            'Brace hard, push floor away.',
            'Stand tall at top.',
            'Hinge down to return bar.'
        ]
    ),
    'Conventional Deadlift': (
        'Standard deadlift stance.',
        [
            'Feet hip-width, hands outside legs.',
            'Hinge and grip bar.',
            'Chest up, back flat.',
            'Drive through floor.',
            'Lock out hips and knees together.'
        ]
    ),
    'Sumo Deadlift': (
        'Wide stance deadlift variation.',
        [
            'Wide stance, hands inside knees.',
            'Push knees out over toes.',
            'Chest up, grip bar.',
            'Push floor apart.',
            'Stand tall at top.'
        ]
    ),
    'Romanian Deadlift': (
        'Hamstring and glute focused hip hinge.',
        [
            'Start standing, bar at thighs.',
            'Push hips back with slight knee bend.',
            'Lower bar along legs.',
            'Feel hamstring stretch.',
            'Drive hips forward to stand.'
        ]
    ),
    'Rack Pull': (
        'Partial deadlift from elevated position.',
        [
            'Set bar on pins at knee height.',
            'Setup like deadlift top position.',
            'Pull bar to lockout.',
            'Control back to pins.',
            'Reset each rep.'
        ]
    ),
    'Back Extension': (
        'Lower back, glutes, and hamstrings.',
        [
            'Set pad at hip crease.',
            'Hinge down with neutral spine.',
            'Extend up to straight line.',
            'Don\'t over-arch.',
            'Squeeze glutes at top.'
        ]
    ),
    'Hyperextension': (
        'Lower back strengthener.',
        [
            'Position hips on pad.',
            'Lower torso down.',
            'Raise up to straight line.',
            'Hold briefly.',
            'Lower with control.'
        ]
    ),
    
    # LEGS
    'Squat': (
        'King of leg exercises.',
        [
            'Bar on upper back, feet shoulder-width.',
            'Brace core, chest up.',
            'Sit down between hips and knees.',
            'Hit depth you can control.',
            'Drive up through whole foot.'
        ]
    ),
    'Back Squat': (
        'Primary quad and glute builder.',
        [
            'Bar on traps/rear delts, grip tight.',
            'Feet shoulder-width, toes slightly out.',
            'Brace, sit down between hips/knees.',
            'Hit depth you can control.',
            'Drive up through heels.'
        ]
    ),
    'Front Squat': (
        'Quad-dominant squat with core emphasis.',
        [
            'Bar on front shoulders, elbows high.',
            'Feet shoulder-width, brace.',
            'Squat down keeping torso upright.',
            'Drive up, elbows stay up.',
            'Maintain front rack position.'
        ]
    ),
    'Hack Squat': (
        'Quad-dominant squat machine.',
        [
            'Back on pad, feet shoulder-width.',
            'Lower sled deep.',
            'Push through mid-foot.',
            'Don\'t lock knees hard.',
            'Control throughout.'
        ]
    ),
    'Smith Machine Squat': (
        'Guided squat for isolation.',
        [
            'Feet slightly forward of bar.',
            'Sit straight down.',
            'Drive up through heels.',
            'Keep bar path vertical.',
            'Control the descent.'
        ]
    ),
    'Leg Press': (
        'Heavy quad and glute work with support.',
        [
            'Position so knees bend deeply without pelvis lifting.',
            'Feet on platform shoulder-width.',
            'Lower sled with control.',
            'Press up without locking knees hard.',
            'Full range of motion.'
        ]
    ),
    'Leg Extension': (
        'Quad isolation exercise.',
        [
            'Align knee with machine pivot.',
            'Lift by extending knees.',
            'Squeeze quads at top.',
            'Lower slow.',
            'Control the negative.'
        ]
    ),
    'Leg Curl': (
        'Hamstring isolation.',
        [
            'Set pad above ankles, align knee pivot.',
            'Curl heels toward butt.',
            'Squeeze hamstrings.',
            'Return slow.',
            'Full range of motion.'
        ]
    ),
    'Lying Leg Curl': (
        'Hamstring curl lying face down.',
        [
            'Lie face down on machine.',
            'Pad behind ankles.',
            'Curl heels to glutes.',
            'Squeeze hamstrings.',
            'Lower with control.'
        ]
    ),
    'Seated Leg Curl': (
        'Seated hamstring isolation.',
        [
            'Sit with back against pad.',
            'Legs extended, pad on calves.',
            'Curl heels under seat.',
            'Squeeze at bottom.',
            'Return controlled.'
        ]
    ),
    'Lunge': (
        'Single-leg strength for glutes and quads.',
        [
            'Step forward, torso tall.',
            'Lower until both knees ~90°.',
            'Push through front foot to stand.',
            'Alternate legs.',
            'Keep balance throughout.'
        ]
    ),
    'Dumbbell Lunge': (
        'Weighted lunge for legs.',
        [
            'Hold dumbbells at sides.',
            'Step forward into lunge.',
            'Lower back knee toward floor.',
            'Push back to start.',
            'Alternate or same leg.'
        ]
    ),
    'Walking Lunge': (
        'Continuous lunging movement.',
        [
            'Step forward into lunge.',
            'Push off and bring back leg forward.',
            'Continue walking pattern.',
            'Maintain upright torso.',
            'Control each step.'
        ]
    ),
    'Reverse Lunge': (
        'Backward stepping lunge.',
        [
            'Step backward into lunge.',
            'Lower back knee toward floor.',
            'Push through front foot.',
            'Return to standing.',
            'Alternate legs.'
        ]
    ),
    'Bulgarian Split Squat': (
        'Brutal unilateral quad and glute exercise.',
        [
            'Rear foot elevated on bench.',
            'Front foot forward.',
            'Lower straight down.',
            'Knee tracks over toes.',
            'Drive up through front foot.'
        ]
    ),
    'Hip Thrust': (
        'Best glute builder.',
        [
            'Upper back on bench, bar on hips (pad it).',
            'Feet flat, shins near vertical at top.',
            'Thrust hips up, ribs down.',
            'Pause and squeeze glutes.',
            'Lower controlled.'
        ]
    ),
    'Glute Bridge': (
        'Glute activation and strength.',
        [
            'Lie on back, knees bent.',
            'Feet flat on floor.',
            'Drive hips up.',
            'Squeeze glutes at top.',
            'Lower with control.'
        ]
    ),
    'Dumbbell Romanian Deadlift': (
        'Hamstrings and glutes with dumbbells.',
        [
            'DBs at thighs.',
            'Push hips back.',
            'Feel hamstring stretch.',
            'Keep back flat.',
            'Stand tall squeezing glutes.'
        ]
    ),
    'Cable Pull-Through': (
        'Glute hinge pattern.',
        [
            'Rope between legs.',
            'Hinge back.',
            'Thrust hips forward.',
            'Squeeze glutes at top.',
            'Control the return.'
        ]
    ),
    'Glute Ham Raise': (
        'Advanced hamstring builder.',
        [
            'Knees on pad, ankles locked.',
            'Lower torso forward.',
            'Pull back up using hamstrings.',
            'Control descent.',
            'Keep hips extended.'
        ]
    ),
    'Nordic Curl': (
        'Extreme hamstring strength.',
        [
            'Kneel with ankles secured.',
            'Lower body slowly forward.',
            'Catch with hands if needed.',
            'Push back up.',
            'Control the negative.'
        ]
    ),
    'Reverse Hyperextension': (
        'Lower back and glutes.',
        [
            'Lie face-down on pad.',
            'Lift legs upward.',
            'Squeeze glutes.',
            'Pause briefly.',
            'Lower controlled.'
        ]
    ),
    'Box Jump': (
        'Explosive leg power.',
        [
            'Stand facing box.',
            'Load hips back.',
            'Jump explosively.',
            'Land softly on box.',
            'Step down and repeat.'
        ]
    ),
    'Calf Raise': (
        'Standing calf builder.',
        [
            'Balls of feet on edge or plate.',
            'Drop heels for stretch.',
            'Rise as high as possible.',
            'Squeeze at top.',
            'Control down.'
        ]
    ),
    'Standing Calf Raise': (
        'Primary calf exercise.',
        [
            'Stand on calf raise machine.',
            'Lower heels for full stretch.',
            'Rise up on toes.',
            'Pause at top.',
            'Lower slowly.'
        ]
    ),
    'Seated Calf Raise': (
        'Seated calf work (more soleus).',
        [
            'Sit with knees bent.',
            'Pad on lower thighs.',
            'Raise heels high.',
            'Lower for full stretch.',
            'Knees stay bent.'
        ]
    ),
    
    # SHOULDERS
    'Overhead Press': (
        'Main shoulder strength press.',
        [
            'Bar at upper chest, hands just outside shoulders.',
            'Brace core and glutes, ribs down.',
            'Press overhead, bar travels close to face.',
            'Lockout with biceps by ears.',
            'Lower controlled.'
        ]
    ),
    'Barbell Overhead Press': (
        'Standing shoulder press.',
        [
            'Bar in front rack position.',
            'Brace core tight.',
            'Press bar overhead.',
            'Full lockout at top.',
            'Lower to shoulders.'
        ]
    ),
    'Military Press': (
        'Strict overhead press.',
        [
            'Feet together, bar at shoulders.',
            'No leg drive allowed.',
            'Press straight overhead.',
            'Full lockout.',
            'Lower with control.'
        ]
    ),
    'Push Press': (
        'Overhead press with leg drive.',
        [
            'Bar at shoulders.',
            'Small dip with legs.',
            'Drive up explosively.',
            'Press bar overhead.',
            'Lower and reset.'
        ]
    ),
    'Dumbbell Shoulder Press': (
        'Shoulder press with dumbbells.',
        [
            'DBs at shoulders, elbows slightly forward.',
            'Press up and slightly in.',
            'Lockout overhead.',
            'Lower slow.',
            'Control both dumbbells.'
        ]
    ),
    'Seated Dumbbell Press': (
        'Seated shoulder press.',
        [
            'Sit with back support.',
            'Dumbbells at shoulder height.',
            'Press overhead.',
            'Lower with control.',
            'Keep core engaged.'
        ]
    ),
    'Arnold Press': (
        'Rotating dumbbell shoulder press.',
        [
            'Start with palms facing you.',
            'Rotate palms forward as you press.',
            'Full lockout overhead.',
            'Reverse the rotation down.',
            'Control throughout.'
        ]
    ),
    'Lateral Raise': (
        'Side delt isolation for width.',
        [
            'Slight lean forward, soft elbows.',
            'Raise DBs to shoulder height.',
            'Lead with elbows.',
            'Pause at top.',
            'Lower slow (no swinging).'
        ]
    ),
    'Dumbbell Lateral Raise': (
        'Side delt builder.',
        [
            'Hold dumbbells at sides.',
            'Raise arms out to sides.',
            'Stop at shoulder height.',
            'Control the descent.',
            'Slight bend in elbows.'
        ]
    ),
    'Cable Lateral Raise': (
        'Constant-tension side delt work.',
        [
            'Handle at low pulley.',
            'Stand sideways to machine.',
            'Raise arm sideways.',
            'Stop at shoulder height.',
            'Lower slow.'
        ]
    ),
    'Rear Delt Fly': (
        'Rear delts and upper back posture.',
        [
            'Hinge forward or use chest-support bench.',
            'Raise arms out to sides.',
            'Squeeze rear delts and upper back.',
            'Lower controlled.',
            'Keep slight elbow bend.'
        ]
    ),
    'Reverse Fly': (
        'Rear delt isolation.',
        [
            'Bent over or chest supported.',
            'Arms hanging down.',
            'Raise out to sides.',
            'Squeeze rear delts.',
            'Lower with control.'
        ]
    ),
    'Cable Rear Delt Fly': (
        'Rear delt isolation with cables.',
        [
            'Cross cables lightly.',
            'Pull arms out wide.',
            'Squeeze rear delts.',
            'Return controlled.',
            'Keep slight bend in elbows.'
        ]
    ),
    'Machine Shoulder Press': (
        'Safe heavy pressing.',
        [
            'Seat adjusted to shoulder height.',
            'Press handles overhead.',
            'Pause at top.',
            'Lower slow.',
            'Keep back against pad.'
        ]
    ),
    'Lateral Raise Machine': (
        'Pure side delt isolation.',
        [
            'Elbows on pads.',
            'Lift outward.',
            'Squeeze at top.',
            'Lower controlled.',
            'Don\'t use momentum.'
        ]
    ),
    'Pike Push-Up': (
        'Shoulder-focused push-up.',
        [
            'Hips high, arms straight.',
            'Body forms inverted V.',
            'Lower head toward floor.',
            'Push back up.',
            'Keep elbows in.'
        ]
    ),
    'Upright Row': (
        'Shoulder and trap builder.',
        [
            'Hold bar or dumbbells.',
            'Pull up along body.',
            'Elbows lead the movement.',
            'Stop at chest height.',
            'Lower with control.'
        ]
    ),
    
    # BICEPS
    'Barbell Curl': (
        'Main biceps builder.',
        [
            'Stand tall, elbows near ribs.',
            'Curl up without swinging.',
            'Squeeze at top.',
            'Lower slow to full extension.',
            'Keep upper arms stationary.'
        ]
    ),
    'EZ-Bar Curl': (
        'Barbell curl with wrist-friendly grip.',
        [
            'Use EZ bar for wrist comfort.',
            'Grip on angled portion.',
            'Curl up with control.',
            'Squeeze biceps.',
            'Lower fully.'
        ]
    ),
    'Dumbbell Curl': (
        'Classic biceps exercise.',
        [
            'Hold dumbbells at sides.',
            'Curl with palms up.',
            'Squeeze at top.',
            'Lower with control.',
            'Alternate or both together.'
        ]
    ),
    'Hammer Curl': (
        'Biceps and brachialis for arm thickness.',
        [
            'Neutral grip (palms facing each other).',
            'Curl up keeping elbows pinned.',
            'Squeeze at top.',
            'Lower slow.',
            'Both arms or alternating.'
        ]
    ),
    'Incline Dumbbell Curl': (
        'Big biceps stretch (long head emphasis).',
        [
            'Sit back on incline bench.',
            'Arms hang straight down.',
            'Curl without moving shoulders.',
            'Squeeze at top.',
            'Lower to full stretch.'
        ]
    ),
    'Cable Curl': (
        'Constant tension biceps curl.',
        [
            'Low cable with bar or rope.',
            'Curl up keeping elbows fixed.',
            'Squeeze hard at top.',
            'Control down.',
            'Don\'t let weight stack touch.'
        ]
    ),
    'Preacher Curl': (
        'Strict biceps isolation.',
        [
            'Upper arms on preacher pad.',
            'Curl bar up.',
            'Squeeze at top.',
            'Lower fully.',
            'Don\'t swing.'
        ]
    ),
    'Concentration Curl': (
        'Isolated single-arm curl.',
        [
            'Sit, elbow on inner thigh.',
            'Curl dumbbell up.',
            'Squeeze bicep hard.',
            'Lower with control.',
            'Complete all reps then switch.'
        ]
    ),
    'Reverse Curl': (
        'Forearms and biceps.',
        [
            'Overhand grip on bar.',
            'Curl up.',
            'Keep elbows fixed.',
            'Lower slow.',
            'Targets brachioradialis.'
        ]
    ),
    'Drag Curl': (
        'Long-head biceps emphasis.',
        [
            'Bar stays close to body.',
            'Elbows move back as you curl.',
            'Drag bar up torso.',
            'Squeeze at top.',
            'Lower controlled.'
        ]
    ),
    'Zottman Curl': (
        'Biceps and forearms combo.',
        [
            'Curl palms up.',
            'Rotate palms down at top.',
            'Lower slowly with overhand grip.',
            'Rotate back to start.',
            'Repeat.'
        ]
    ),
    '21s': (
        'Biceps curl intensity technique.',
        [
            '7 reps bottom half.',
            '7 reps top half.',
            '7 reps full range.',
            'No rest between.',
            'Maximum pump.'
        ]
    ),
    'Spider Curl': (
        'Strict biceps isolation.',
        [
            'Lie chest on incline bench.',
            'Arms hang straight down.',
            'Curl up.',
            'Squeeze at top.',
            'Lower fully.'
        ]
    ),
    
    # TRICEPS
    'Tricep Pushdown': (
        'Triceps isolation with cable.',
        [
            'Elbows pinned to sides.',
            'Push down to full extension.',
            'Squeeze triceps.',
            'Return slow.',
            'Don\'t let elbows drift forward.'
        ]
    ),
    'Cable Pushdown': (
        'Cable triceps isolation.',
        [
            'Stand at high cable.',
            'Elbows at sides.',
            'Push down to lockout.',
            'Squeeze triceps.',
            'Control return.'
        ]
    ),
    'Rope Pushdown': (
        'Triceps pushdown with rope.',
        [
            'Grip rope attachment.',
            'Push down and split rope at bottom.',
            'Squeeze triceps.',
            'Control return.',
            'Keep elbows stationary.'
        ]
    ),
    'Skullcrusher': (
        'Triceps long head and overall size.',
        [
            'Lie on bench, weight above chest.',
            'Bend elbows, lower toward forehead.',
            'Keep upper arms still.',
            'Extend back to top.',
            'Control throughout.'
        ]
    ),
    'Lying Tricep Extension': (
        'Lying triceps builder.',
        [
            'Lie on bench with bar or dumbbells.',
            'Arms extended over chest.',
            'Lower weight toward head.',
            'Extend arms back up.',
            'Keep elbows pointed up.'
        ]
    ),
    'Overhead Tricep Extension': (
        'Long head stretch and growth.',
        [
            'Weight overhead (DB or cable).',
            'Lower behind head by bending elbows.',
            'Keep elbows fairly close.',
            'Extend back up fully.',
            'Feel the stretch.'
        ]
    ),
    'Dumbbell Tricep Extension': (
        'Single or double arm overhead extension.',
        [
            'Hold dumbbell overhead.',
            'Lower behind head.',
            'Keep elbow pointed up.',
            'Extend to lockout.',
            'Control the weight.'
        ]
    ),
    'Tricep Dip': (
        'Bodyweight triceps builder.',
        [
            'Hands on bench or bars.',
            'Lower body by bending elbows.',
            'Keep body close to bench.',
            'Push up to lockout.',
            'Focus on triceps.'
        ]
    ),
    'Bench Dip': (
        'Triceps dip using bench.',
        [
            'Hands on bench behind you.',
            'Feet on floor or elevated.',
            'Lower body down.',
            'Push back up.',
            'Keep close to bench.'
        ]
    ),
    'Diamond Push-Up': (
        'Triceps-focused push-up.',
        [
            'Hands together forming diamond.',
            'Lower chest to hands.',
            'Push back up.',
            'Keep body straight.',
            'Elbows close to body.'
        ]
    ),
    'Dip Machine': (
        'Triceps press machine.',
        [
            'Sit upright.',
            'Press handles down.',
            'Lock out elbows.',
            'Return slow.',
            'Maintain posture.'
        ]
    ),
    'Tricep Kickback': (
        'Triceps isolation.',
        [
            'Hinge forward, arm bent.',
            'Extend arm straight back.',
            'Squeeze tricep at top.',
            'Lower with control.',
            'Keep upper arm stationary.'
        ]
    ),
    'Cable Kickback': (
        'Cable tricep kickback.',
        [
            'Low cable, hinge forward.',
            'Extend arm back.',
            'Squeeze at lockout.',
            'Return controlled.',
            'Keep elbow fixed.'
        ]
    ),
    
    # CORE
    'Plank': (
        'Core bracing and endurance.',
        [
            'Forearms on floor, elbows under shoulders.',
            'Body straight from head to heels.',
            'Glutes tight, abs braced.',
            'Hold without hips sagging.',
            'Breathe steadily.'
        ]
    ),
    'Side Plank': (
        'Oblique stability.',
        [
            'Forearm on floor, body sideways.',
            'Hips lifted, body straight.',
            'Hold position.',
            'Don\'t let hips drop.',
            'Switch sides.'
        ]
    ),
    'Crunch': (
        'Basic ab flexion.',
        [
            'Lie on back, knees bent.',
            'Hands behind head.',
            'Curl shoulders off floor.',
            'Squeeze abs.',
            'Lower with control.'
        ]
    ),
    'Cable Crunch': (
        'Weighted ab flexion.',
        [
            'Rope on high pulley, kneel facing stack.',
            'Crunch ribs toward hips.',
            'Don\'t just bow down.',
            'Squeeze abs at bottom.',
            'Return controlled.'
        ]
    ),
    'Hanging Knee Raise': (
        'Lower abs and hip flexors.',
        [
            'Hang with shoulders down.',
            'Raise knees to chest.',
            'Pause at top.',
            'Lower slow without swinging.',
            'Control momentum.'
        ]
    ),
    'Hanging Leg Raise': (
        'Advanced lower ab exercise.',
        [
            'Hang with control.',
            'Raise straight legs.',
            'Pause at top.',
            'Lower slow.',
            'Minimize swing.'
        ]
    ),
    'Toes-to-Bar': (
        'Advanced hanging leg raise.',
        [
            'Hang tight from bar.',
            'Raise feet to touch bar.',
            'Control descent.',
            'Avoid excessive swinging.',
            'Full range each rep.'
        ]
    ),
    'Russian Twist': (
        'Obliques and rotational core.',
        [
            'Sit with lean back slightly.',
            'Feet up or on floor.',
            'Rotate side to side.',
            'Control the movement.',
            'Keep chest up.'
        ]
    ),
    'Decline Sit-Up': (
        'Full range abdominal exercise.',
        [
            'Feet locked on decline bench.',
            'Sit all the way up.',
            'Control down.',
            'Keep core tight.',
            'Don\'t use momentum.'
        ]
    ),
    'Woodchopper': (
        'Rotational core strength.',
        [
            'Cable set high or low.',
            'Pull diagonally across body.',
            'Rotate torso.',
            'Brace core.',
            'Return slow.'
        ]
    ),
    'Cable Woodchopper': (
        'Cable rotational exercise.',
        [
            'High or low cable attachment.',
            'Rotate and pull diagonally.',
            'Keep arms extended.',
            'Control the motion.',
            'Work both sides.'
        ]
    ),
    'Pallof Press': (
        'Anti-rotation core stability.',
        [
            'Stand sideways to cable.',
            'Press handle straight out.',
            'Resist rotation.',
            'Hold briefly.',
            'Return controlled.'
        ]
    ),
    'Ab Rollout': (
        'Anti-extension ab exercise.',
        [
            'Kneel with wheel or bar.',
            'Roll forward extending body.',
            'Brace core hard.',
            'Pull back using abs.',
            'Don\'t hyperextend back.'
        ]
    ),
    'Dead Bug': (
        'Core stability exercise.',
        [
            'Lie on back, arms up.',
            'Knees at 90 degrees.',
            'Lower opposite arm and leg.',
            'Keep lower back pressed down.',
            'Alternate sides.'
        ]
    ),
    'Bird Dog': (
        'Core and back stability.',
        [
            'On hands and knees.',
            'Extend opposite arm and leg.',
            'Keep back flat.',
            'Hold briefly.',
            'Alternate sides.'
        ]
    ),
    'Mountain Climber': (
        'Core cardio exercise.',
        [
            'Start in push-up position.',
            'Drive knees toward chest.',
            'Alternate legs quickly.',
            'Keep hips down.',
            'Maintain pace.'
        ]
    ),
    'Leg Raise': (
        'Lower ab exercise.',
        [
            'Lie flat on back.',
            'Legs straight.',
            'Raise legs to vertical.',
            'Lower with control.',
            'Keep lower back down.'
        ]
    ),
    'Sit-Up': (
        'Classic ab exercise.',
        [
            'Lie on back, knees bent.',
            'Hands across chest or behind head.',
            'Sit all the way up.',
            'Lower with control.',
            'Don\'t anchor feet if possible.'
        ]
    ),
    'V-Up': (
        'Advanced ab exercise.',
        [
            'Lie flat, arms overhead.',
            'Simultaneously lift legs and torso.',
            'Touch toes at top.',
            'Lower with control.',
            'Keep legs straight.'
        ]
    ),
    
    # FOREARMS
    'Wrist Curl': (
        'Forearm flexor exercise.',
        [
            'Forearms supported on bench.',
            'Palms up.',
            'Curl wrists up.',
            'Squeeze.',
            'Lower slow.'
        ]
    ),
    'Reverse Wrist Curl': (
        'Forearm extensor exercise.',
        [
            'Forearms supported.',
            'Palms down.',
            'Lift knuckles up.',
            'Pause.',
            'Lower controlled.'
        ]
    ),
    'Farmer Walk': (
        'Grip strength and full-body tension.',
        [
            'Grab heavy weights.',
            'Stand tall.',
            'Walk with control.',
            'Don\'t lean.',
            'Set down safely.'
        ]
    ),
    'Farmer Carry': (
        'Loaded carry for grip and core.',
        [
            'Pick up heavy dumbbells or handles.',
            'Stand tall, shoulders back.',
            'Walk for distance or time.',
            'Maintain posture.',
            'Grip hard.'
        ]
    ),
    'Plate Pinch': (
        'Grip strength exercise.',
        [
            'Pinch weight plates together.',
            'Thumb on one side.',
            'Hold for time.',
            'Keep thumb firm.',
            'Switch hands.'
        ]
    ),
}


def populate_exercises():
    """Update exercises with descriptions and instructions."""
    updated = 0
    not_found = []
    
    for name, (description, steps) in EXERCISE_DATA.items():
        # Try exact match first
        exercises = Exercise.objects.filter(name__iexact=name)
        
        # Try partial match if no exact match
        if not exercises.exists():
            exercises = Exercise.objects.filter(name__icontains=name.split()[0])
            if name.split()[-1] not in ['Press', 'Curl', 'Raise', 'Row', 'Fly']:
                exercises = exercises.filter(name__icontains=name.split()[-1])
        
        if exercises.exists():
            for exercise in exercises:
                if not exercise.description:  # Only update if empty
                    exercise.description = description
                    exercise.instructions = json.dumps(steps)
                    exercise.save()
                    updated += 1
                    print(f"Updated: {exercise.name}")
        else:
            not_found.append(name)
    
    print(f"\nTotal updated: {updated}")
    if not_found:
        print(f"Not found ({len(not_found)}): {not_found[:10]}...")


if __name__ == '__main__':
    populate_exercises()
