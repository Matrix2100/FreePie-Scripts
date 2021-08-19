verify = 0
if starting:  
    system.setThreadTiming(TimingTypes.HighresSystemTimer)
    system.threadExecutionInterval = 5
    
    def set_button(button, key):
        if keyboard.getKeyDown(key):
            v.setButton(button, True)
        else:
            v.setButton(button, False)
    
    def calculate_rate(max, time):
        if time > 0:
            return max / (time / system.threadExecutionInterval)
        else:
            return max

    int32_max = (2 ** 14) - 1
    int32_min = (( 2** 14) * -1) + 1
    
    v = vJoy[0]
    v.x, v.y, v.z, v.rx, v.ry, v.rz, v.slider, v.dial = (int32_min,) * 8
    
    # =============================================================================================
    # Axis inversion settings (multiplier): normal = 1; inverted = -1
    # =============================================================================================
    global throttle_inversion, braking_inversion, clutch_inversion
    throttle_inversion = 1
    braking_inversion = 1
    clutch_inversion = 1
    
    # =============================================================================================
    # Ignition cut settings
    # =============================================================================================
    global ignition_cut_time, ignition_cut_elapsed_time
    ignition_cut_enabled = True
    ignition_cut_time = 100
    ignition_cut_elapsed_time = 0
    
    global ignition_cut, ignition_cut_released
    # Init values, do not change
    ignition_cut = False
    ignition_cut_released = True
    
    # =============================================================================================
    # Mouse and Steering settings
    # =============================================================================================
    global mouse_sensitivity, sensitivity_center_reduction
    sensitivity_center_reduction = 1 #IDK WHAT'S THAT DUDE
    mouse_sensitivity = 2.1 # obviously, mouse sensitivity... this will change the general turn speed
    
    global steering, steering_max, steering_min, steering_center_reduction    
    steering = 0.0 # Init values, do not change
    steering_max = float(int32_max) # Init values, do not change
    steering_min = float(int32_min) # Init values, do not change
    steering_center_reduction = 1 # Init values, do not change
    
    # ==================================
    # Steering Acelerator Settings     =
    # ==================================
    global using_steering_acelerator
    using_steering_acelerator = True #True to enable, False to disable
    
    sa_multiplier = 1
    sa_a = 3.5 # changes the curve inclination (1:/, 3:U)
    sa_b = 6 # changes how faster the curve will grow up to max value
    sa_c = 4000 # changes how early the max value will be acheved, until 16000 but 4000 is already nice
    
    def steering_acelerator(steering_position):
    	global verify
    	virefy = 1
    	if steering_position == 0:
    		return 1
    	elif abs(steering_position)/sa_c < 1:
            verify = abs(steering_position)/sa_c
            return float((((abs(steering_position)/sa_c)**sa_a)/sa_b)+1)*sa_multiplier
        else:
            verify = abs(steering_position)/sa_c
            return float((((abs(steering_position)/sa_c)**sa_a)/sa_b)+1)*sa_multiplier
	
   	# ==================================
    # Steering Return Rate Settings    =
    # ==================================
    global using_return_rate
    
    using_return_rate = True #True to enable, False to disable
    sr_a = 0.005 # that's the point where deadzone will end (yes, that's a very low value)
    sr_b = 5 # increase the top point (this function is like a mountain /\)
    sr_c = 3000 # That's when the return rate will stop changing (6000 its like 30% of the steering wheel)
    sr_d = 1 # return rate multiplier
    sr_e = 3 # reduces the minimum value for the return rate (you'll need to compensate that changing the sr_b)
    return_rate_multiplier = 10 # 0 <> 2 
    def steering_return_value(steering_position):
    	x = abs(steering_position/sr_c)
    	if ( abs(steering_position)/steering_max > 0.008):
    		return float(0.025*(x**(2-(x*sr_b)))+sr_e)*sr_d
    	else:
    		return 0.3
	
    # =============================================================================================
    # Throttle settings
    # =============================================================================================
    global throttle_blip_enabled
    throttle_blip_enabled = True
    
    # In milliseconds
    throttle_increase_time = 300
    throttle_increase_time_after_ignition_cut = 0 #idk whats that
    throttle_increase_time_blip = 50 #neither that
    throttle_decrease_time = 100
    
    global throttle, throttle_max, throttle_min
    # Init values, do not change
    throttle_max = int32_max * throttle_inversion
    throttle_min = int32_min * throttle_inversion
    throttle = throttle_min
    
    #def calculate_rate(max, time):
    #    if time > 0:
    #        return max / (time / system.threadExecutionInterval)
    #    else:
    #        return max
    sr_a = 4 # This will change the curve angle, making the throttle be multiplied for higher values when close to the incrase time maximum
    sr_b = 3 # This will incrase the maximum value for this function
    sr_c = 1 # This is about the minimum value, if you set to 0.8 you'll acelerate slower at the moment where you start acelerating (1 is default incrase)
    sr_d = 1 # Just a generic multiplier on the multiplier for lazy uses......
    def throttle_rate_multiplier(x):
    	x = abs(x)
    	if (x < 1):
    		return float(((x**sr_a)/sr_b)+sr_c)*sr_d
    	else:
    		return float(((1**sr_a)/sr_b)+sr_c)*sr_d
    		
    global throttle_increase_rate, throttle_decrease_rate
    # Set throttle behaviour with the increase and decrease time,
    # the actual increase and decrease rates are calculated automatically
    throttle_increase_rate = calculate_rate(throttle_max, throttle_increase_time)
    throttle_increase_rate_after_ignition_cut = calculate_rate(throttle_max, throttle_increase_time_after_ignition_cut) 
    throttle_increase_rate_blip = calculate_rate(throttle_max, throttle_increase_time_blip)
    throttle_decrease_rate = calculate_rate(throttle_max, throttle_decrease_time) * -1
    
    # =============================================================================================
    # Braking settings
    # =============================================================================================
    int32_max_break = ((2 ** 14) - 1)*0.75
    # In milliseconds
    braking_increase_time = 220
    braking_decrease_time = 150
    
    global braking, braking_max, braking_min
    # Init values, do not change
    braking_max = int32_max_break * braking_inversion
    braking_min = int32_min * braking_inversion
    braking = braking_min
    
    global braking_increase_rate, braking_decrease_rate
    # Set braking behaviour with the increase and decrease time,
    # the actual increase and decrease rates are calculated automatically
    braking_increase_rate = calculate_rate(braking_max, braking_increase_time)
    braking_decrease_rate = calculate_rate(braking_max, braking_decrease_time) * -1
    
    # =============================================================================================
    # Clutch settings
    # =============================================================================================   
    # In milliseconds
    clutch_increase_time = 0
    clutch_decrease_time = 50
    
    global clutch, clutch_max, clutch_min
    # Init values, do not change
    clutch_max = int32_max * clutch_inversion
    clutch_min = int32_min * clutch_inversion
    clutch = clutch_min
    
    global clutch_increase_rate, clutch_decrease_rate
    # Set clutch behaviour with the increase and decrease time,
    # the actual increase and decrease rates are calculated automatically
    clutch_increase_rate = calculate_rate(clutch_max, clutch_increase_time)
    clutch_decrease_rate = calculate_rate(clutch_max, clutch_decrease_time) * -1

# assign button
vJoy[0].setButton(0,int(keyboard.getKeyDown(Key.Q)))
vJoy[0].setButton(1,int(keyboard.getKeyDown(Key.D)))
vJoy[0].setButton(2,int(keyboard.getKeyDown(Key.E)))
vJoy[0].setButton(3,int(keyboard.getKeyDown(Key.L)))
vJoy[0].setButton(4,int(keyboard.getKeyDown(Key.W)))
vJoy[0].setButton(5,int(keyboard.getKeyDown(Key.V)))
vJoy[0].setButton(6,int(keyboard.getKeyDown(Key.Space)))
vJoy[0].setButton(7,int(keyboard.getKeyDown(Key.A)))


# =================================================================================================
# LOOP START
# =================================================================================================

# =================================================================================================
# Steering logic
# =================================================================================================
if steering > 0:
    steering_center_reduction = sensitivity_center_reduction ** (1 - (steering / steering_max))
elif steering < 0:
    steering_center_reduction = sensitivity_center_reduction ** (1 - (steering / steering_min))

# ==================================
# Steering Return Rate Logic       =
# ==================================
if using_return_rate == True: 
	if steering > 0 and mouse.deltaX <= 0:
		steering = steering - steering_return_value(steering)/ steering_center_reduction
		return_value = steering_return_value(steering)
	elif steering < 0 and mouse.deltaX >= 0:
		steering = steering + steering_return_value(steering)/ steering_center_reduction
		return_value = steering_return_value(steering)
		

# ==================================
# Steering Acelerator Logic        =
# ==================================
if using_steering_acelerator == True:
	#value = 
	#if value >= steering_max: value = steering_max-1
	steering = steering + (((float(mouse.deltaX) * mouse_sensitivity)*steering_acelerator(steering)) / steering_center_reduction)
else:
	steering = steering + (float(mouse.deltaX) * mouse_sensitivity) / steering_center_reduction

if steering > steering_max:
    steering = steering_max
elif steering < steering_min:
    steering = steering_min

v.x = int(round(steering))

# =================================================================================================
# Clutch logic
# =================================================================================================
if keyboard.getKeyDown(Key.E):
	clutch = clutch + clutch_increase_rate
else:
    clutch = clutch + clutch_decrease_rate

if clutch > clutch_max * clutch_inversion:
    clutch = clutch_max * clutch_inversion
elif clutch < clutch_min * clutch_inversion:
    clutch = clutch_min * clutch_inversion

v.z = clutch

# =================================================================================================
# Throttle logic
# =================================================================================================
if mouse.leftButton:
	if throttle <= throttle_max:
		throttle = throttle + throttle_increase_rate*throttle_rate_multiplier(throttle)
else:
	if throttle >= throttle_min:
		throttle = throttle + throttle_decrease_rate

v.y = throttle

# =================================================================================================
# Braking logic
# =================================================================================================
if mouse.rightButton:
	if braking <= braking_max:
		braking = braking + braking_increase_rate
else:
	if braking >= braking_min:
		braking = braking + braking_decrease_rate

v.rz = braking

# =================================================================================================
# Buttons post-throttle logic
# =================================================================================================
#set_button(look_left_button, look_left_key)
#set_button(look_right_button, look_right_key)
#set_button(look_back_button, look_back_key)
#set_button(change_view_button, change_view_key)
#set_button(indicator_left_button, indicator_left_key)
#set_button(indicator_right_button, indicator_right_key)

# =================================================================================================
# PIE diagnostics logic
# =================================================================================================
diagnostics.watch(v.x)
diagnostics.watch(v.y)
diagnostics.watch(v.rz)
diagnostics.watch(v.slider)

diagnostics.watch(mouse.deltaX)
diagnostics.watch(steering)
diagnostics.watch(verify)
diagnostics.watch(steering_acelerator(steering))
diagnostics.watch(steering_return_value(steering))
