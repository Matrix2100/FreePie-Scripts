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
    float_max = (2 ** 13.5) - 1
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
    # Mouse settings
    # =============================================================================================
    global mouse_sensitivity, sensitivity_center_reduction
    mouse_sensitivity = 2.7
    sensitivity_center_reduction = 1
    
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
    # Steering settings
    # =============================================================================================
    global steering, steering_max, steering_min, steering_center_reduction    
    # Init values, do not change
    steering = 0.0
    steering_max = float(int32_max)
    steering_min = float(int32_min)
    steering_center_reduction = 1
    
    #change to adjust return rate function variables ==============================================
    return_rate_multiplier = 4
    #function 0 <> 2 / 0 ^ 5
    return_value = 0
    var_max_return_rate = 3.2 #increase max return rate value
    def steering_return_value(x_var):
      return (3*(x_var**(3-(x_var*var_max_return_rate)-2.5)))*return_rate_multiplier

    
    
    
    
    # =============================================================================================
    # Throttle settings
    # =============================================================================================
    global throttle_blip_enabled
    throttle_blip_enabled = True
    
    # In milliseconds
    throttle_increase_time = 250
    throttle_increase_time_after_ignition_cut = 0
    throttle_increase_time_blip = 50
    throttle_decrease_time = 100
    
    global throttle, throttle_max, throttle_min
    # Init values, do not change
    throttle_max = int32_max * throttle_inversion
    throttle_min = int32_min * throttle_inversion
    throttle = throttle_min
    
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
    # In milliseconds
    braking_increase_time = 270
    braking_decrease_time = 150
    
    global braking, braking_max, braking_min
    # Init values, do not change
    braking_max = float_max * braking_inversion
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

#return logic ---

if steering > 0 and mouse.deltaX <= 0:
	steering = steering - steering_return_value(abs(steering/steering_max)*2)/ steering_center_reduction
	return_value = steering_return_value(abs(steering/steering_max)*2)
elif steering < 0 and mouse.deltaX >= 0:
	steering = steering + steering_return_value(abs(steering/steering_min)*2)/ steering_center_reduction
	return_value = steering_return_value(abs(steering/steering_min)*2)

# end return logic ---


steering = steering + ((float(mouse.deltaX) * mouse_sensitivity) / steering_center_reduction)

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
    throttle = throttle + throttle_increase_rate
else:
	throttle = throttle + throttle_decrease_rate

if throttle > throttle_max * throttle_inversion:
    throttle = throttle_max * throttle_inversion
elif throttle < throttle_min * throttle_inversion:
    throttle = throttle_min * throttle_inversion

v.y = throttle

# =================================================================================================
# Braking logic
# =================================================================================================
if mouse.rightButton:
    braking = braking + braking_increase_rate
else:
    braking = braking + braking_decrease_rate

if braking > braking_max * braking_inversion:
    braking = braking_max * braking_inversion
elif braking < braking_min * braking_inversion:
    braking = braking_min * braking_inversion

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
diagnostics.watch(return_value)
diagnostics.watch(mouse.deltaX)
diagnostics.watch(steering)
diagnostics.watch(throttle_blip_enabled)
diagnostics.watch(ignition_cut_enabled)