def check_afm(afm):
    """ 
    Checks the integrity of the personal tax number.
 
    Author: marmako@gmail.com
    """
    if afm.isdigit() == False:
        msg  = "Το ΑΦΜ: {0} δεν είναι έγκυρο.\n".format(afm)
        msg += "Πρέπει να αποτελείται ΜΟΝΟ από ψηφία."
        print(msg)
        return False
 
    elif len(afm) != 9:
        msg  = "Το ΑΦΜ: {0} δεν είναι έγκυρο.\n".format(afm)
        msg += "Πρέπει να έχει εννέα ψηφία."
        print(msg)
        return False
 
    else:
        chck_numbers = [256, 128, 64, 32, 16, 8, 4, 2, 1]
        length = len(chck_numbers) - 1
        athroisma = 0
 
        for i in range(length):
            athroisma += (int(afm[i]) * chck_numbers[i])
 
        ch_digit = int(afm[-1])  
 
        ypoloipo = (athroisma % 11) % 10
 
        if ypoloipo == ch_digit :
            return True
        else:
            return False
