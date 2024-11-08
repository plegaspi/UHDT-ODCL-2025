# create a optimized payload matching algortihm 

# taking in a list of objects and number of how accurate it matches with every object need to correctly identify them
target_ratio_list = [['payload1',0.8,0.7,0.6, 0.4,0.3 ], ['payload2',0.2,0.3,0.4,0.5,0.7], ["payload3",0.6,0.8,0.9,0.2,0.65]]


matched_target_list = []

# make a list of the possible objects
while len(target_ratio_list)>0:

    sports_ball = [target_ratio_list[0][1], "sports_ball"]
    person_man = [target_ratio_list[0][2], 'manequin']
    motorcycle = [target_ratio_list[0][3], 'motorcycle']
    airplane = [target_ratio_list[0][4], 'airplane']
    bus = [target_ratio_list[0][5], 'bus']
    #boat = ['boat']
    #stop_sign = ['stop_sign']
    print(bus[0])

    #define ratio 
    matched_target = sports_ball

    #compare with each object and find the highest ratio number

    if matched_target[0] < person_man[0]:
        matched_target =person_man
    else: 
        pass
    if matched_target[0] < motorcycle[0]:
        matched_target =motorcycle
    else:
         pass
    if matched_target[0] < airplane[0]:
        matched_target =airplane
    else:
         pass
    if matched_target[0] < bus[0]:
        matched_target =bus
    else:
         pass
    '''
    if matched_target[0] < motorcycle[0]:
        matched_target =motorcycle
    else:
         pass
    '''

    print(matched_target[1])
    #put in list of correctly matched targets
    matched_target_list.append(matched_target)

    #remove the target and go to the next one
    target_ratio_list.pop(0)


print(matched_target_list)

