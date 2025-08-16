



The BBC Microcomputer
Teletext System
User Guide
Part no 404000
Issue no 1
Date June 1983


WARNING: THE TELETEXT ADAPTER MUST BE EARTHED
Important: The wires in the mains lead for the Teletext Adapter are coloured in accordance with 
the following code:
Green and yellow
Earth
Blue
Neutral
Brown
Live
As the colours of the wires may not correspond with the coloured markings identifying the 
terminals in your plug, proceed as follows:
The wire which is coloured green and yellow must be connected to the terminal in the plug which 
is marked by the letter E, or by the safety earth symbol + or coloured green, or green and yellow.
The wire which is coloured blue must be connected to the terminal which is marked with the 
letter N, or coloured black.
The wire which is coloured brown must be connected to the terminal which is marked with the 
letter L, or coloured red.
If the socket outlet available is not suitable for the plug supplied, the plug should be cut off and 
the appropriate plug fitted and wired as previously noted. The moulded plug which was cut off 
should be disposed of as it would be a potential shock hazard if it were to be plugged in with the 
cut off end of the mains cord exposed. The moulded plug must be used with the fuse and fuse 
carrier firmly in place. The fuse carrier is of the same basic colour* as the coloured insert in the 
base of the plug. Different manufacturers' plugs and fuse carriers are not interchangeable. In the 
event of loss of the fuse carrier, the moulded plug MUST NOT be used. Either replace the 
moulded plug with another conventional plug wired as previously described, or obtain a 
replacement fuse carrier from an authorised BBC Microcomputer dealer. In the event of the fuse 
blowing it should be replaced, after clearing any faults, with a 3 amp fuse that is ASTA approved 
to BS1362.
*Not necessarily the same shade of that colour.
© Copyright Arnie Computers Limited 198:1
Neither the whole or any part of the information contained in, or the product described in, this manual may be adapted or 
reproduced in any material form except with the prior written approval of Acorn Computers Limited (Acorn Computers).
The product described in this manual and products for use with it. are subject to continuous development and improvement. All 
information of a technical nature and particulars of the product and its use (including the information and particulars in this 
manual) are given by Acorn Computers in good faith. However, it is acknowledged that there may be errors or omissions in this 
manual. A list of details of any amendments or revisions to this manual can be obtained upon request from Acorn Computers 
Technical Enquiries. Acorn Computers welcome comments and suggestions relating to the product and this manual.
All correspondence should be addressed to:
Technical Enquiries
Acorn Computers Limited
Fulbourn Road
Cherry Hinton
Cain Midge CB1 4JN
All maintenance and service on the product must be carried out by Acorn Computes' authorised dealers. Acorn Computers can 
accept no liability whatsoever for any loss or damage caused by service or maintenance by unauthorised personnel. This manual in 
intended only to assist the reader in the use of the product, and therefore Acorn Computers shall not be liable for any loss or 
damage whatsoever arising from the use of any information or particulars in, or any error or omission in, this manual, or any 
incorrect use of the product.
First published 198:1
Published by Acorn Computers Limited, Fulbourn Road, Cherry Hinton. Cambridge CB1 4JN
Typeset by Bateman Typesetters. Cambridge
Printed by Saunders & Williams, Croydon


Contents
1 About this User Guide
1
2 What is Teletext?
3 What does the BBC Microcomputer
Teletext System do?
3
3.1 Introduction
3
3.2 Terminal mode
3
3.3 Telesoft mode
4
3.4 Assembler level
4
4 Getting started
5
4.1 Connecting up the units
5
4.2 General information on the format of commands
8
4.3 Tuning in the Teletext Adapter
8
4.4 A first attempt at Telesoftware
11
Downloading a disordered program
12
Downloading an ordered program
13
5 Using the system in Terminal mode
14
5.1 Introduction
14
5.2 Terminal mode commands
14
Selecting a channel
14
Fine tune
15
Select a page
15
Keep a page
15
Release a kept page
16
Select the last explicit page
16
Select index page
16
Reveal and conceal
16
Save a page to file
17
Load a page from file
17
Hold page
18
Enter * command
18
Exit to previous language
18


Exit to Telesoft mode
19
Select wild card
19
5.3 Accessing linked pages
20
6 Using the system in Telesoft mode
23
6.1 Introduction
23
6.2 Telesoft mode commands
25
*BBC1, *BBC2
25
*CH1, *CH2, *CH3, *CH4
26
*DATE
27
*DISPLAY
27
*EXEC
28
*HELP
29
*ITV1, *ITV2
29
*OPT0
30
*OPT1
30
*OPT2
31
*OPT3
32
*PAGE
33
*TIME
34
*TRANSFER
34
*TUNE
35
7 Using the Teletext system at assembly level
36
7.1 Teletext assembly level interface
36
7.2 Teletext OSWORD calls
38
8 Changing the filing system
41
9 Technical information
42
9.1 The structure and numbering of Teletext pages
42
9.2 Teletext signals
44
Rows 1 to 23
45
Row 0
45
Rows 24 to 31
46
Page check word (row 27)
46
9.3 Character codes
48
Display modes
48
Colour
48
Flashing and concealed characters
49


Double height
49
Hold graphics control
49
9.4 Reference
49
9.5 The television service data packet
49
Byte structure of the television service data packet
50
Bytes 1 to 6 – decoder information
50
Bytes 7 to 12
51
Bytes 13 and 14 – channel identification
51
Byte 15 – time offset
51
Bytes 16 to 18 – modified Julian date
51
Bytes 19 to 21 – coordinated universal time
52
Bytes 26 to 45 – status display message
52
9.6 The Telesoftware format
52
Names
52
Command subroutines
57
Start block and medium description commands
59
Start block <DSB>
59
Teletext <TXT>
60
End block <DEB>
60
File and segment information commands
60
End of file <DET>
60
Title of file <DTL>
61
Comment <DCO>
61
Ignore <DIG>
61
Load address (absolute) <DLA>
62
Load address (relative) <DLR>
62
Execution address (absolute) <DXA>
62
Execution address (relative) <DXR>
62
Inhibit run <DIR>
63
Define data type <DDT>
63
Format redefinition commands
63
Change escaped-name's meaning (decoded string) <DES>
63
Change escaped-name's meaning (command) <DEC>
63
Change lone-name's meaning (decoded string) <DLS>
64
Change lone-name's meaning (command) <DLC>
64
No reversion to default format before next file <DND>
64
Revert to default format <DEF>
64
The escape operator <ESC>
64
Eight-bit byte adjustment
65
Eight-bit byte adjustment (lower) <ULB>
65
Eight-bit byte adjustment (raise) <URB>
65


Error in transmission <UER>
65
Figures
4.1 Connecting the Teletext Adapter
7
4.2 Rear view of the Teletext Adapter
10
4.3 Tuning picture format
10
5.1 Linked pages
21
9.1 Byte structure of Teletext rows 1 to 23
45
9.2 Contiguous and separated graphics modes
48
Tables
9.1 Teletext character codes
47
9.2 Name tables — default entries
54
9.3 The command subroutines
59
Appendices
Appendix 1
Installing the TELEROM into the BBC Microcomputer
66
Appendix 2
Teletext reception
69
Appendix 3
Summary of Terminal mode commands
71
Appendix 4
A statement about Telesoftware by the BBC
72
IMPORTANT
IF YOU ARE RECEIVING TELETEXT ON AN ORDINARY TELEVISION 
RECEIVER, YOU ARE COVERED BY YOUR EXISTING TELEVISION LICENCE, 
WHICH OF COURSE MUST BE VALID. IF YOU DO NOT HAVE A TELEVISION 
RECEIVER BUT ARE RECEIVING TELETEXT WITH THE AID OF A VIDEO 
MONITOR UNIT, YOU MUST HAVE A COLOUR OR BLACK AND WHITE 
TELEVISION LICENCE DEPENDING ON WHETHER YOUR MONITOR IS 
COLOUR OR BLACK AND WHITE.


1 About this User
Guide 
This User Guide contains all the information you need to use the BBC Microcomputer 
Teletext System. Whilst it is essentially an operating manual, the User Guide contains 
certain technical information which will help you to understand generally what 
Teletext is all about and gain some appreciation of the future potential offered by this 
system.
Chapters 2 and 3 are introductory. Chapter 2 explains briefly what Teletext is all about 
and chapter 3 deals briefly with the various ways in which you can use your BBC 
Microcomputer with the Teletext service.
Chapter 4, as its title suggests, gets you started. It explains how to connect up the 
system, tune into Teletext and quickly run a Telesoftware program.
Chapters 5, 6 and 7 contain the detailed instructions for using the system in the three 
modes of operation: Terminal, Telesoft and assembly level.
Chapter 8 explains how to select, as the current system, the various filing systems (
including Telesoft) which may be available on your computer.
Chapter 9 contains information which will probably be of interest to the more 
technically minded user, but which is not essential for using the system.


2 What is Teletext?
Teletext is a service offered by the BBC and IBA which makes available a wide variety 
of information through the medium of television. This information could be share 
prices on the stock market or the latest football results; the possibilities are almost 
endless.
Teletext information is transmitted from BBC and IBA television transmitters and can 
be received on a commercial television receiver suitably equipped with a Teletext 
Adapter unit. The transmitted signal however, unlike a normal television signal, is in 
digital form which makes it additionally suitable for use with the BBC Microcomputer.
The total amount of Teletext information is too large to be displayed on a television 
screen at any one instant and for this reason it is transmitted in `pages' rather like the 
pages of a book. Only one page at a time can be displayed on a television screen.
A page of information may contain text, symbols or a mixture of both; it depends on 
the type of information and how the broadcasters decide to present it.
Because of the amount and variety of information available, transmitted Teletext pages 
are organised and numbered in such a manner so as to enable you quickly and easily to 
locate and display specific items of information.


3 What does the
BBC Microcomputer
Teletext System do? 
3.1 Introduction
The BBC Microcomputer Teletext System gives you most of the facilities of an 
ordinary Teletext receiver and, in addition, the service known as Telesoftware.
Telesoftware is a service similar to Teletext and is transmitted in the same 
manner, that is, in pages. However, these pages contain computer programs. A 
program will consist of one or more pages, depending on the program length, 
and each program has its own file name by which it is identified. These 
programs, once received, are decoded by the Teletext Adapter and thereafter 
are available to the computer for display, storage on disc/tape or immediate 
execution.
It is emphasised that your television set does not require a Teletext decoder. 
This function amongst others is performed by the Teletext Adapter.
There are three main ways in which you can use the system: in Terminal mode, 
in Telesoft mode or at assembler level. The following is a brief description of 
the facilities offered by each.
3.2 Terminal mode
`Terminal mode' is a program which Acorn has supplied to give you easy 
access to Teletext pages. It also lets you use some more sophisticated features 
which only an 'intelligent' receiver can offer. These features include asking for 
pages in advance, having pages stored by the system before you ask for them (
see the section on linked pages), and being able to save pages onto any 
available filing system for later examination.
You can also use Terminal mode as an easy way of finding and loading `
Telesoftware' computer programs.
You cannot write programs whilst in Terminal mode. In addition, if you are 
using a television receiver, you cannot display Teletext pages and television 
programmes simultaneously.


4 What does the BBC Microcomputer Teletext System do?
3.3 Telesoft mode
An important feature of Teletext transmissions is the ability to send programs, or '
software', with the Teletext service. In keeping with the philosophy of BBC 
Microcomputer products, Acorn has produced a filing system interface as the means of 
accessing Telesoftware files.
IT IS IMPORTANT that you appreciate that Telesoft is a filing system, and not an 
applications program such as Terminal mode. With Telesoft selected you will not be 
able to save programs as the system thinks you are trying to save data to the television 
channel!
You may think of Telesoft as a 'read-only' tape; it is quite a good analogy.
In addition to Telesoftware, you can also display and store Teletext pages. However the 
full range of Terminal mode commands is not available and it is therefore probably 
more convenient to return to Terminal mode should you wish to handle Teletext pages.
You can write and run your own programs whilst in Telesoft mode, but to store these 
programs you should select the appropriate filing system, ie disc or tape. See section 8.
3.4 Assembler level
Assembly code level allows you to control the Teletext system using programs written 
in Assembly Language. You can enter these into the computer from the keyboard or 
from file. There are two main areas of control: one is concerned with the filing system, 
and the other with the Teletext Adapter.
The filing system function allows the storage and retrieval of Telesoftware files. You 
can control this by the standard interfaces to the Machine Operating System, which are 
independent of the filing system.
The Teletext Adapter functions, which control the conditions under which a file is 
stored and executed, can be accessed via the general purpose Machine Operating 
System calls.


4 Getting started
Before proceeding further, check that you have the following items:
–
A Model B BBC Microcomputer fitted with a BASIC ROM.
–
A Teletext Adapter with the following items attached:
A power cable with a 13A 3-pin plug fitted to it.
A 'ribbon' cable terminating in a 34-way plug.
–
A coax cable fitted with a phono plug and a UHF plug as supplied with the 
BBC Microcomputer (if you're using a normal television receiver), or a 
coax cable fitted with the appropriate connectors (if you're using a video 
monitor).
–
A Teletext ROM (TELEROM).
You will not need a new aerial lead, as the existing television aerial lead can 
be used.
If any of the above are missing, contact your local supplier quoting the order 
number which was given to you when you first placed your order. This number 
also appears on the dispatch label on the outside of the packing case.
4.1 Connecting up the units
The first thing to do is to make sure that the ROMs are correctly positioned on 
the microcomputer circuit board and then to fit the TELEROM. The 
instructions for doing this are in Appendix 1, however if you do not feel 
sufficiently confident, take your microcomputer and TELEROM to an 
authorised dealer who will do it for you.
Next, refer to Fig 4.1 which shows the microcomputer and Teletext Adapter 
connected together and connect up the system as follows:
1. Connect the 34-way socket on the Teletext Adapter 'ribbon' cable to the 
plug labelled 1 MHz BUS on the computer.
Caution: This socket may fit both ways round–the correct way is with the 
arrow at one end of the socket aligned with the arrow next to the '1 MHz BUS' 
label. IF THE SOCKET WILL NOT GO RIGHT IN EXAMINE THE PLUG 
AND SOCKET FOR DAMAGE AND OBSTRUCTIONS. DO NOT USE 
EXCESSIVE FORCE.


6 Getting started
2. Disconnect the aerial lead from the back of your television set and 
reconnect it to the standard television aerial socket on the back of the Teletext 
Adapter.
Note: An aerial which stands on top of your television set does not generally 
provide a strong enough signal. You will in all probability need a loft or 
externally mounted aerial. If you think your aerial may not be good enough 
refer to Appendix 2 which may assist you, or consult your dealer.
3. Connect up whatever storage units you are using (ie disc or cassette) to the 
computer.
4. Connect the computer UHF OUTPUT socket to the aerial socket on your 
television set using the phono plug/UHF plug cable, or connect the computer 
VIDEO OUT or RGB OUT socket to the input socket on the video monitor.
5. Connect the television, storage unit, microcomputer and Teletext Adapter to 
the mains supply, if possible using adjacent sockets for Teletext Adapter and 
computer.
6. Switch on television/video monitor, Teletext Adapter unit, microcomputer 
and storage device (disc or cassette) if fitted. IT IS IMPORTANT THAT 
THE TELETEXT ADAPTER IS SWITCHED ON BEFORE THE 
MICROCOMPUTER. Your television screen should now display the 
following message:
BBC Computer 32K
Acorn TFS
BASIC
>_
The current filing system is Telesoft (TFS).
Note 1: If Acorn TFS no power appears, check that you have connected the 
adapter correctly and that it is switched on at the rear. Press BREAK before 
continuing. If this still fails to produce the start-up message, check the 
position of the ROMs on the microcomputer circuit board (see Appendix 1).
Note 2: The Teletext software incorporates a 'power-down' mode so that if, 
when you switch on the microcomputer, the Teletext Adapter is switched


Getting started 7
off, the message Acorn TFS no power will be displayed. This means that the 
Teletext software is inactive and therefore the memory space it would normally 
occupy is free to be used for running large programs.
If you switch on the Teletext Adapter after the microcomputer, the Teletext 
software is not automatically activated; you must press the BREAK key first.
If you switch off the Teletext Adapter whilst the microcomputer is 'on', the 
Teletext software is not automatically de-activated; you must press the BREAK
key first.
Note 3: If the positioning of the ROMs is such that Telesoft is not the default 
filing system, press the T key, hold it down and press BREAK , then release 
BREAK then T This will cause the correct start-up message to be displayed 
without re-positioning the ROMs as detailed in Appendix 1.
Once the correct start-up message is displayed you can now go ahead and tune 
the Teletext Adapter.
Fig 4.1 Connecting the Teletext Adapter


8 Getting started
4.2 General information on the format of commands
Note 1: Most of the commands are put into the computer by pressing one of 
the ten red keys labelled f0 to f9, either on its own or together with the SHIFT
key. In the latter case it is important that you press the keys in the following 
manner otherwise the command will never go into the computer:
— Press the SHIFT key, keep it held down and press the red function key.
— Release the f key, then release the SHIFT key.
If you do attempt to input a faulty command the computer will usually tell 
you, with a message on the screen, what to do and how to get back to a normal 
situation.
Note 2: Throughout the guide there are many instructions on how to type in 
commands to the computer and what the correct response is. The following 
applies to these instructions:
— Where you see a word in brackets thus, <word>, this is describing what 
you have to type in, eg <file name> means you have to type in the name of 
a file. Do not type in the brackets.
— Where you see a word 'reversed out' this means you have to press a 
specific key, eg TAB means press the TAB key.
— Where the text is an actual message displayed on your monitor screen it is 
shown in computer typeface, eg the message ***Waiting is displayed. 
Likewise in a command the characters in computer typeface are to be 
typed in exactly as shown, eg type in *EXEC.
4.3 Tuning in the Teletext Adapter
There are four channels built into the Teletext Adapter and assigned numbers 
1 to 4. We recommend that you allocate these channels as follows:
Channel 1 — BBC1
Channel 2 — BBC 2
Channel 3 — ITV1
Channel 4 — ITV2
The procedure for tuning in the system to receive each channel is as follows:


Getting started 9
1. Type in *TELETEXT then press the RETURN key. 
The message ***Waiting for page is displayed.
2. Press the f4 key.
The prompt Channel should now appear on the screen.
3. Type in 1 (to select channel 1), then press the RETURN key.
The message ***Waiting for page is again displayed.
4. Press the SHIFT and f4 keys together.
Your screen will display a station tuning scale (see Fig 4.3). On top of the 
tuning scale sits a tuning bar which indicates the strength of received 
Teletext. Maximum signal strength is when the tuning bar is as long as the 
scale (100
5. Turn the number 1 tuning control on the rear of the Adapter (Fig 4.2) to 
one end of its travel (this is indicated by a 'clicking' as you turn the control). 
Now very slowly turn the control over its full travel. You will see the tuning 
bar suddenly increase in length as you tune in to a BBC or ITV Teletext 
channel. This is accompanied by the channel and page numbers at the top of 
the screen. When you have found the longest tuning bar together with the 
messages CEEFAX and CH1 you are correctly tuned in to channel 1. 
REMEMBER YOU CAN RECEIVE ALL FOUR TELETEXT CHANNELS 
ON EACH TUNING CONTROL SO MAKE SURE YOU GET THE RIGHT 
CHANNEL.
6. Press the SPACE BAR on your keyboard and repeat steps 2 to 5 for 
channels 2, 3 and 4. The only differences are:
— In step 3, type in the appropriate channel number (2, 3 or 4).
— In step 5, rotate the appropriate control number (2, 3 or 4).
7. When you have tuned in all four channels press the SPACE BAR . This 
will remove the tuning scale and a Teletext index page will be automatically 
displayed. This is the default page and is discussed in section 5.2.
Now that your system is working we suggest that you have a go at running 
one of the Telesoftware programs being transmitted, the procedure for which 
is given in the next section (4.4). You will need to use only a few Terminal 
mode commands and it should give you confidence to use the full range of 
features which are explained later in the guide.


10 Getting started
Fig 4.2 Rear view of the Teletext Adapter
Fig 4.3 Tuning picture format


Getting started 11
4.4 A first attempt at Telesoftware
Assuming that you're carrying on from the previous section your screen 
should be displaying an index page. If on the other hand you've just switched 
on the equipment then you must enter Teletext by typing in *TELETEXT then 
pressing the RETURN key. The CEEFAX channel 1 index page will be 
displayed.
Next select a channel (any channel) by first pressing the f4 key. This results in 
the message Channel being displayed. Then type in the channel number (1, 
2, 3 or 4) and finally press RETURN . The message ***Waiting for page
will be displayed until it is replaced by the index page for the channel you've 
selected.
Do this a few times to get the idea, then try selecting a page.
You can select a page by pressing the f0 key, then typing in the page number 
you want (three digits) then pressing RETURN . You may have to wait a 
short while before the page you have selected appears. Again we suggest you 
try this a few times to get the idea.
When you feel confident, select channel 1 then page 700. This will display a 
list of the currently transmitted Telesoftware programs and the page on which 
each can be found. Decide which program you want, then select the page it is 
stored on.
The next thing to do is to download the program, that is, load it into the 
computer ready to be run. To download the program, press the SHIFT and f9
keys together. What happens next may not make a great deal of sense and so 
deserves some explanation.
As you are probably aware programs can be structured in two very different 
ways and this affects what happens when they are downloaded.
Programs structured in numbered lines can be loaded in any order since the 
computer will organise the lines into the correct numerical sequence prior to 
running the program. A program structured in such a way is said to be a 
disordered file.
A program structured as merely a series of statements (with no numbered 
lines) must be loaded into the computer starting at the first statement and 
exactly in the order in which it has been written. This is because there are no 
numbered lines for the computer to organise as there are for disordered files. 
Such a program is said to be an ordered file.


12 Getting started
Another point to bear in mind is that whilst programs are listed as being on 
consecutively numbered pages, almost always a program will be longer than 
one page. For example there are currently several programs being transmitted 
on page 702 onwards, however they are all longer than one page.
Let's assume that the program listed under page 704 is in fact 12 pages long. 
This means that it will take 12 transmissions of page 704 to get the entire 
program into the computer and this can take quite a long time. It follows 
therefore that the earlier in the transmission sequence you try to download the 
program, the longer it takes to get round to page one again and this can 
significantly affect how long you have to wait before an ordered program is 
loaded (see below).
What happens during downloading depends on whether the program is 
ordered or disordered and is explained in the following:
Downloading a disordered program
As soon as the SHIFT and f9 keys have been pressed, the message 
Searching is displayed. This tells you that the system is looking for a page in 
the program.
Immediately a page (any page) in the program is received, the message 
disappears and the contents of the page 'scroll' up the screen as they are loaded 
into computer memory.
When the page has been completely loaded, the message Searching is again 
displayed until another page in the program is found.
This process continues until the program is completely loaded, whereupon the 
message Loaded is displayed and an audible 'bleep' sounds.
During downloading the normal transmitted Teletext page headers are 
displayed to indicate (during waiting) that your Teletext Adapter is still 
functioning.
When the decoder is loading Telesoftware, it checks the validity of data on 
each page it receives. If this check shows up an error, you will see the 
message Bad data. Retrying. . .
This usually means you will have to wait until this page comes round again in 
the transmission cycle, but you may be lucky if the bad page was one you 
have already received or if it was a title page with no software on it. If you 
wait long enough you will always be able to load a Telesoftware program, 
unless your reception is particularly bad.


5 Using the system in
Terminal mode 
5.1 Introduction
We recommend that you spend a few minutes using the select a page and 
select a channel commands, before going on to the rest of the commands.
You may find it a good idea to read first section 9.1 which explains in some 
detail how Teletext pages are numbered and how the entire Teletext 
transmission is structured. This may help you to understand the various 
commands you are about to use.
5.2 Terminal mode commands
First enter Terminal mode by typing in *TELETEXT and pressing the 
RETURN key. A default channel, BBC1 CEEFAX, is selected and a default 
index page is displayed. In addition to news and information, the following 
standard items are usually displayed on your screen:
–
Channel title and page number (header), eg CEEFAX XXX, at the top left.
–
The page number you have selected at the top far left.
–
The changing page number at the left of centre.
–
The date and time at the far right.
Selecting a channel
Press the f4 key.
The prompt Channel is displayed.
Type in 1, 2, 3 or 4.
This number appears after Channel.
Press RETURN (to select the channel).
The only thing which happens immediately on the screen is that the channel 
title and changing page header now correspond to the newly-selected channel. 
A default index page for the new channel is displayed as soon as it is received.


Using the system in Terminal mode 15
Fine tune
This is the same function you used when tuning the Teletext Adapter (see 4.3). 
You can use it anytime to display the tuning scale if the quality of the 
displayed Teletext page deteriorates.
Press the f4 and SHIFT keys together.
When you have finished tuning, press the SPACE BAR to inhibit the tuning 
routine and display the page.
Select a page
To display a transmitted page:
Press the f0 key.
Type in the page number which can be three digits or seven digits (see section 
9.1 on page numbering).
Press the RETURN key.
Note: Make sure you have selected a page which is being transmitted.
Until the selected page is reached, the previous page and the message 
***Waiting for page is displayed.
Keep a page
This function allows you to store the displayed page in computer memory. 
Thereafter, every time this particular page is received, it updates the stored 
page. In this manner, a 'kept' page is continuously updated and can be 
displayed immediately by using the normal 'select a page' command. You can '
keep' a page before it has actually arrived and select another page while you 
are waiting. In this way you can ask for more than one page at a time. To keep 
a page:
Press the f3 key.
The message Page kept is displayed at the bottom of the screen.
Note: When you attempt this command, the message Buffer full — please 
release a page may appear. This means that all available memory for 
keeping pages is used up and you must first release a page, before trying to 
keep a page. The following explains how to release a kept page.


16 Using the system in Terminal mode
Release a kept page
This function causes the displayed page to be lost provided it is a kept page. 
To release the kept page:
Press the SHIFT and f3 keys.
The message Page released is displayed.
Select the last explicit page
If you are displaying linked pages (see 5.3) you can quickly return to the last 
page which was displayed by the explicit typing in of its number. This is 
usually the first page in the linked structure.
Press the f1 key.
The last explicitly selected page is displayed.
Select index page
You can return to the default index page which was automatically displayed 
when you first entered the current channel.
Press the f1 and SHIFT keys together.
Note: If no default index page number is being transmitted on your current 
channel, then page #00 will be selected instead (see 'Select wild card').
Reveal and conceal
Some pages are transmitted with certain text 'hidden', ie concealed as spaces. 
For example, the answers to a quiz. Any page with hidden data will display a 
message something like Press the REVEAL key. To reveal this hidden text:
Press the f2 key.
The hidden text appears, and the page itself is 'held' so that it cannot be 
updated by subsequent transmitted pages.
To conceal the text and cancel the 'hold' state: Press 
the SPACE BAR .
To conceal the text but retain the page 'hold' state: Press 
the SHIFT and f2 keys together.


Using the system in Terminal mode 17
Save a page to file
This function allows you to store the displayed page under any file name onto 
the currently selected filing system, such as cassette or disc.
Press the f7 key.
The message Save file is displayed.
Type in <the file name> and press RETURN .
The page is stored in a file. When storage is complete, the page is displayed 
with the file name under which you have just stored it, together with the 
message Press space to continue.
When you press the SPACE BAR , the same page continues to be displayed, 
but the file name is removed, and the changing headers are again displayed.
If you attempt this with Telesoft as your currently selected filing system, the 
message Illegal operation will be displayed. (This is due to the fact that 
Telesoft is a 'read only' filing system, therefore you cannot save anything to 
this filing system.)
To recover from this situation, press the ESCAPE key. Now select another 
filing system such as disc or tape by using the Enter * command facility 
described below. You can now save the data to this filing system as described 
immediately above ('Save a page to file').
Load a page from file
This function allows you to display any page which is currently stored under 
a file name.
Press the f6 key.
The message Load file is displayed.
Type the file name of the page for display, then press RETURN .
The page is then displayed, together with its file name.
Note that the page headers stop changing and the message Press space to 
continue is displayed.
When you press the SPACE BAR , the file name disappears and the page 
headers again start to change.


18 Using the system in Terminal mode
Hold page
This function holds any displayed page and prevents it from changing. This is 
a useful function to have if you are saving or loading rolling pages or wild 
card pages (which are likely to change very quickly). To hold a page:
Press the f8 key.
The displayed page is held in its current state.
To cancel the 'hold' state:
Press the SPACE BAR .
The page is now free to be updated.
Enter * command
This allows you to remain in Terminal mode and at the same time use those * 
commands which relate to the operating system. These commands are shown 
on page 416 of the BBC Microcomputer System User Guide. In addition, you 
have available for use all commands associated with the particular ROMs 
fitted to your microcomputer, eg the disc filing system.To enter a command:
Press key f5
The prompt * is displayed at the bottom of your screen.
Type in the appropriate command and press RETURN .
The message Press space to continue is displayed.
if you wish to enter other * commands, ignore the Press space to 
continue message and repeat as above.
To return to the last displayed page press the SPACE BAR .
Exit to previous language
Press the f9 key.
The start-up message for the language previously selected (from which 
Teletext was entered) is displayed and the system is now controlled by this 
language ROM.


Using the system in Terminal mode 19
Note: If you have pressed the BREAK key whilst in Terminal mode, your 
previous language will be Teletext Terminal mode and the f9 key will cause 
this to be re-entered.
Exit to Telesoft mode
If you select a page containing a Telesoftware program, this function puts the 
system automatically into Telesoft mode and causes the program to be loaded 
into computer memory page by page. You can then go ahead and run the 
program. To exit to the Telesoft filing system and execute a program:
Press the SHIFT and f9 keys together.
The program will start to load into computer memory as soon as the first page 
is received. If you start this function say halfway through the program 
transmission then it may be a few minutes before the program starts to load (
see section on ordered/disordered loading).
Select wild card
This enables you to select specified sequences of numbered pages for display (
including their sub-pages, if any). We know that each page has a three-digit 
number. The function allows you to specify any combination of one or two of 
these three digits as part of a page number to be displayed. The unspecified 
digit(s) can be any number, ie completely `wild'. For example, if you specified 
34#, all page numbers whose first digit is 3 and whose second digit is 4 will be 
displayed. Theoretically this would be 340, 341, 342 etc to 349. But bear in 
mind that not all pages are transmitted.
To select a wild card press the f0 key (as you would do when normally 
selecting a page) then type in three characters (which may be any combination 
of digits and #s), then press RETURN .
The specified wild card pages will be displayed as and when they are received, 
with a small built-in delay between consecutive pages to give you time to hold 
a page.


20 Using the system in Terminal mode
5.3 Accessing linked pages
Now that you know how to display any transmitted page of Teletext, we will 
explain how you can display pages which, because of their information 
content, are related to each other. These are known as linked pages.
A Teletext page displays 24 rows of text or graphic information. However 
more rows may be transmitted which are not displayed on the screen but 
which contain information for the Teletext decoder. In particular, row 27 
contains information in the form of numbers which point to related (linked) 
pages. These numbers are called links.
Take a look at Fig 5.1. The headlines page has four links, each pointing to a 
lead page. In this case row 27 of the headlines page would contain four link 
numbers, link 1 pointing to lead page 1 and so on. You will see also that each 
lead page has links, each of which points to page 1 of a related story. For 
example, lead 3 has three links pointing to page 1 of stories 3A, 3B and 3C, so 
row 27 of lead 3 would contain link numbers 1, 2 and 3. This system of links 
extends to the last page in each story then back round to the first page as is 
shown by stories 3A and 1.
The microcomputer looks at row 27 of the page, detects the link numbers and 
loads as many of the linked pages as it can fit into memory. Although you 
cannot see these pages, they are being continuously updated. If for example 
you selected the headlines page on Fig 5.1, the microcomputer would load the 
four linked lead pages into its memory and these would then be available for 
display.
Let's suppose you are currently displaying the headlines page which can be 
done using the 'select a page' method previously discussed. The headlines 
page will show four links. To select one of the linked pages, type in the link 
number (1, 2, 3 or 4). The message Link n (where n is the number you typed) 
will be displayed. Now press the RETURN key. The message Waiting for 
link n will be displayed until it is replaced by the selected linked page. 
Suppose you select lead 3 for display. This has three links pointing to three 
story pages, and again you can select any one.
Only link numbers 0-23 are valid and the system will reject an invalid number 
by sounding a 'bleep'. If you select a link number which, although valid, is not 
shown on the current page, the message No such link will be displayed 
when you press the RETURN key. If the current page has no links, the 
message No links present will be displayed.


Using the system in Terminal mode 21
Fig 5.1 Linked pages


22 Using the system in Terminal mode
Let's assume that by using the links you have arrived at a page with only one 
link. This could be lead 1 or page 1 of story 3A. You can now use the key 
marked v to 'step' forwards through the story, page by page. You can also step 
back one level by using the ^ key, but to return to the top-level index page 
you need to use the 'last explicit page' key f1.
If we look again at Fig 5.1 there are routes marked *. These connect together 
adjacent pages at the same level in the structure. You can easily display an 
adjacent page at the same level by pressing the <- or -> keys (whichever is 
appropriate). For example if you are currently displaying lead 3 and you wish 
to display lead 2, simply press the <- key. This is useful if you wanted only to 
glance at the leader of each story but not go to any depth. The thing to 
remember is that, unlike links, these routes are not displayed, so you must 
remember how many links the page immediately higher in the structure has 
and this will tell you how many adjacent pages there are. For example if you 
are displaying page 1 of story 3A the fact that lead 3 has three links tells you 
that there is a total of three adjacent pages.
You may see the messages Cannot go left and Cannot go right when 
using the <- and -> keys. This will happen if the current link is 0 or 23 
respectively, since you are in fact requesting an invalid link.


6 Using the system in
Telesoft mode 
6.1 Introduction
This mode provides a series of commands for dealing specifically with 
Telesoftware as distinct from Teletext. Some of the commands, eg `select a 
page', are much the same as in Teletext mode, however commands are not 
available in this mode for specifically dealing with normal Teletext pages, 
such as the 'reveal' command and the commands to save pages to another 
filing system and select linked pages. You can if you wish view normal 
Teletext pages in this mode but it is more convenient to do so in the Terminal 
mode. You should only enter Telesoft mode when you wish to deal with 
Telesoftware files.
You will recall that in chapter 4 we suggested that as a first step, you try to run 
one of the Telesoft programs before going on to use the full range of Terminal 
mode commands. We suggest that you now do something similar before going 
on to use the full range of Telesoftware commands.
What follows is a simple procedure which tells you how to get a Telesoftware 
program running using some of the Telesoft commands. To the home 
computer user it is quite often unclear just why certain commands are 
necessary at certain times and what they do. In the following simple procedure 
we have attempted to go at least some way to correcting this problem by 
putting in explanations as and where we felt it would help you.
The first thing to do is get into Telesoft mode. You can do this by typing in:
*TELESOFT and pressing RETURN .
The prompt >_ is displayed.
The Telesoft mode is now the current filing system until another is entered (
see chapter 8: Changing the filing system).
While in Telesoft mode, the computer will understand and respond to the 
commands discussed in this chapter. Apart from these commands, the 
computer will behave in the same way as before entering Telesoft mode: thus 
you can still write programs while in Telesoft mode.
Now select BBC 1 channel by typing in:


24 Using the system in Telesoft mode
*BBC1 and pressing RETURN .
As before the prompt >_ will be displayed.
Once you have selected the channel you want, you can then go on to select the 
page you want, 700 in this case, by typing in:
*PAGE 700 and pressing RETURN .
After typing this command, page 700 will become the currently selected page 
and will be subject to all subsequent commands until a new page is selected (
page 700 is currently the Telesoftware index page).
The next step is to get the page you've just selected into memory. Until this is 
done you can't display it. However, you first need to make sure that you do not 
overwrite a program already in memory. The command you will use to put the 
page in memory is TRANSFER. You will cause the page selected to be loaded 
in an area of 960 bytes immediately before HIMEM (HIMEM defines the start 
of screen memory). Page 414 of the BBC Microcomputer User Guide explains 
how RAM is allocated and 415 shows where spare memory is located. To find 
the address in memory at which you can start loading the page, type in:
HIMEM = HIMEM - 960 and press RETURN . Then type in PRINT 
~HIMEM and press RETURN (where ~ indicates a hexadecimal value).
The address displayed (which is in hexadecimal) is the one you will need to 
use in the TRANSFER command (next).
Next, transfer the page into memory by typing in: 
*TRANSFER <address> and press RETURN .
When the prompt >_ appears, the page has been captured and stored in 
memory at the address specified.
Now display the page, by typing:
*DISPLAY <address> and pressing RETURN
where <address> is the one used in the *TRANSFER command.
The page will be immediately displayed, listing the file name of each 
Telesoftware program being transmitted, together with the page number on 
which each can be found. When you have decided which program you want to 
run, select the page using the *PAGE command described previously, then 
type in:
*EXEC <file name> and press RETURN .


Using the system in Telesoft mode 25
Refer to 4.4 of this manual which explains what happens when you download 
a program. Having downloaded the program, you can now run it by typing in:
RUN and pressing RETURN .
The program will now run.
This completes the introductory procedure. The full range of Telesoft 
commands is in the next section.
6.2 Telesoft mode commands
The Telesoft filing system provides a number of commands which allow you 
to control the Teletext Adapter and manipulate the captured program.
All the commands can be typed in from the keyboard or included in a BASIC 
program. Each command is described separately under the following headings:
Description
What the command does in functional terms.
Syntax
The actual command words and the order in which 
commands and data are arranged.
Example
An example of a string of commands including the one 
described.
Note: As with any other BBC Microcomputer filing system, Telesoft allows 
you to type abbreviations for its commands, such as *TE. for *TELETEXT, or 
*TELES. for *TELESOFT.
*BBC1
*BBC2
Description
These commands are used to select channels 1 and 2 for Teletext reception.
Syntax
*BBC1
*BBC2
Example
*TELESOFT
*BBC2


26 Using the system in Tele soft mode
This will cause channel 2 to be selected. The appearance of >_ confirms 
the selection.
Notes
It is up to the user to ensure that channel 1 is tuned to BBC 1 and channel 2 is 
tuned to BBC2 for this command to produce the expected results.
*CH1
*CH2
*CH3
*CH4
Description
These commands are used to select one of the four available channels for 
Teletext reception.
Syntax
*CH1
*CH2
*CH3
*CH4
Example
*TELE SOFT
*CH3
This will cause channel 3 to be selected.
Notes
These commands are alternatives to the *BBC and *ITV commands and 
should be used where the channels are not tuned to the recommended stations, 
ie channel 1 to BBC1 etc.


Using the system in Telesoft mode 27
*DATE
Description
This command causes the date, as transmitted by the television service data 
packet (see 9.5), to be displayed.
Syntax 
*DATE
Example
*TELE SOFT 
*BBC1
*DATE
Notes
Date information is extracted from the television service data packet (TSDP). 
If the TSDP is not transmitted or the data is corrupt on reception an error 
message is displayed.
*DISPLAY
Description
This command is used to display any Teletext page which has previously 
been transferred into memory with a *TRANSFER command.
Syntax
*DISPLAY <address>
where <address> is the hexadecimal address used in the *TRANSFER 
command.
Example
*TELE SOFT
*BBC2
*PAGE 200
*TRANSFER 7000 
*DISPLAY 7000
This will cause BBC2 CEEFAX page 200 to be displayed on the screen.


28 Using the system in Telesoft mode
Notes
The address specified must be in hexadecimal and should correspond exactly 
to an address used for a previous *TRANSFER command. Several pages may 
be transferred to separate memory locations before display.
*EXEC
Description
This command is used to execute a stream of ASCII characters from a 
Telesoftware file as though they have been entered from the keyboard. These 
ASCII characters may be a BASIC program or keyboard commands.
Syntax
*EXEC <file name>
*EXEC ""
Example
*TELE SOFT
*BBC1
*PAGE 704
*EXEC "WELCOME"
This will cause the Telesoftware program WELCOME on BBC1 CEEFAX 
page 704 to be executed.
Notes
If the file name is given as a null string then the first program found on the 
selected page will be executed.
Beware: If you have specified a non-existent file name the system will wait for 
ever trying to find it.


Using the system in Telesoft mode 29
*HELP
Description
This command is used to display useful information about Telesoft mode, 
Terminal mode or the computer system in general.
Syntax
*HELP (For general computer system information) *HELP 
TELETEXT (For Terminal mode information) *HELP TELESOFT (
For Telesoft mode information) *HELP OPT (For information about 
user-definable options)
Example
*HELP TELETEXT
This will display a list of all Terminal mode commands, together with a short 
description of each and the function keys used to call up the command.
Notes
If the Teletext Adapter is not switched on, help on the Teletext system will not 
be available.
*ITV1
*ITV2
Description
These commands are used to select channels 3 and 4 for Teletext reception.
Syntax
*ITV1
*ITV2
Example
*TELE SOFT 
*ITV2
*PAGE 400


30 Using the system in Telesoft mode
This will cause page 400 of channel 4 to become the currently selected page.
Notes
It is up to the user to ensure that channel 3 is tuned to ITV and channel 4 to 
CHANNEL 4 for this command to have the expected results.
*OPT0
Description
This command sets all options to their default values.
Syntax 
*OPT0
Example
*TELESOFT
*BBC2
*PAGE 220
*OPT0
*EXEC "PROG"
Notes
The default settings are:
*OPT1,128
*OPT2,1
*OPT3,0
*OPT1
Description
Telesoftware files can include information which is displayed whilst the file is 
being loaded. This displayed information, as well as 'searching' messages, can 
be controlled with the *OPT1 command as follows:


Using the system in Telesoft mode 31
*OPT1,0
No messages displayed
1,1
Title displayed
1,2
Language and title displayed
1,3
Computer type and all above items displayed
1,4
Date of file publication and all above items displayed
1,5
Source or author of file and all above items displayed 1,128 
'Searching' messages and all above items displayed
Syntax *OPT1,
<parameter>
Example
*TELESOFT
*BBC1
*PAGE 703
*OPT1,2
*EXEC""
This will cause a load of the first program transmitted on BBC1 CEEFAX 
page 703 to be executed, and the program language and title to be displayed.
Notes
The default setting is *OPT1,128, ie all messages are displayed.
The title is a concise description of what the file contains. This is not 
necessarily the same as the file name which is merely a label to identify the 
file.
*OPT2
Description
This command controls the steps taken when the system encounters an error 
whilst reading a Telesoftware file. *OPT2,0 causes the system to ignore 
errors, *OPT2,1 causes the system to retry for a page until it has been 
received correctly and *OPT2,2 causes the system to abort the downloading if 
an error is detected.
Syntax *OPT2,
<parameter>


32 Lasing the system in Telesoft mode
Example
*TELESOFT
*BBC1
*PAGE 708 
*OPT2,1
*EXEC ""
This causes the first Telesoftware file found on page 708 of BBC1 CEEFAX 
to be executed, and in the case of a reception error for the page to be re-
loaded.
Notes
Errors may be encountered in the checkbytes (see section 9.2) of the page 
header, data parity or page CRC checks. In the first instance single bit errors 
are automatically corrected by the system. Parity or CRC errors can not be 
corrected and the system will retry for the page if *OPT2,1 is set. Pressing 
ESCAPE will cause the retries to abort.
*OPT3
Description
When a Telesoftware load is started all previously redefined protocol bytes are 
reset to their original values, but this feature may be suppressed so that a 
format may be learned from loading one program, then re-used for loading a 
second. *OPT3,1 disables this reset feature and *OPT3,0 re-enables it.
Syntax
* OPT3,<parameter>
Example
*TELESOFT
*BBC1
*PAGE 707
*EXEC "PROG1"
*OPT3,1
*EXEC "PROG2"


34 Using the system in Telesoft mode
*TIME
Description
This command causes the time of day, as transmitted by the television 
service data packet (see 9.5), to be displayed.
Syntax
*TIME
Example
*TELESOFT
*BBC1
*TIME
Notes
Time information is extracted from the television service data packet (TSDP). 
If the TSDP is not transmitted or the data is corrupt on reception, an 
appropriate error message is displayed.
*TRANSFER
Description
This command transfers the current page to a given memory location.
Syntax
*TRANSFER <address>
Example
*TELE SOFT
*BBC1
*PAGE 100
*TRANSFER 6800
This transfers BBC1 CEEFAX page 100 to memory starting at location &6800.
Notes
The page must have been selected with the *PAGE command before issuing 
this command.


Using the system in Telesoft mode 35
*TUNE
Description
This command invokes the fine tuning routine for the currently selected 
channel.
Syntax 
*TUNE
Example
*TELESOFT
*ITV1
*TUNE
This will invoke the fine tuning routine for channel 3.
Notes
The fine tuning routine is the same as that entered by SHIFT and f4 in 
Terminal mode, as described in section 4.3.


7 Using the Teletext
system at assembly
level
7.1 Teletext assembly level interface
This section describes the calls available at assembly level which give the 
advanced programmer more control over the Teletext Adapter than is possible 
in Terminal mode. These calls are available from both Assembly Language 
and BASIC.
The Teletext system is accessed through the general purpose routine ''
OSWORD' whose entry point is address &FFF1 in the BBC Microcomputer 
Machine Operating System.
OSWORD calls in which register A contains the value 122 (&7A) are 
Teletext-specific calls – they are obeyed only when the Telesoft filing system 
is selected. A typical example of such a call (first in BASIC then in Assembly 
Language) is given below. This is the call to select the TV channel from which 
Teletext is received, which in this example is BBC1.
The description in the manual is a cryptic '[&8B, channel]'. This means that 
the parameter to OSWORD is a control block containing the two 1-byte values 
'&8B' and 'channel' respectively. The values of the registers on the call to 
OSWORD have a fixed significance:
–
A is always the 'Teletext OSWORD number', ie &7A.
–
X and Y are always treated as a concatenated value containing the 16-bit 
address of the control block in which the actual parameters are stored. (X 
is the low byte and Y is the high byte.)
–
P is irrelevant (except that the processor should not be in decimal mode).
Control blocks have various formats – the only fixed slot being the first byte 
which serves a dual purpose:
–
To identify the specific Teletext command wanted.
–
To return the status of the operation (as a success/failure code, typically 0 
meaning OK, or 17 meaning escape).
To allow for future enhancements of the Teletext system, control blocks 
should be declared as being exactly 16 bytes long.


Using the Teletext system at assembly level 37
Please note that the error codes are command dependent.
Example 1: Calling the Teletext system from BASIC
OSWORD = &FFF1
DIM parameter 15
parameter?0 = &8B
parameter?1 = 0 :REM 0 —> BBC1, 1 —> BBC2 etc.
A% = &7A
X% = parameter MOD 256
Y% = parameter DIV 256
PYXA% = USR (OSWORD)
Example 2: Calling the Teletext system from Assembly 
Language
DIM CodeSpace 100
OSWORD = &FFF1
FOR Pass = 0 TO 2 Step 2
P% = CodeSpace [OPT Pass
.SelectBBC1
Lda #&8B
Sta parameter
Ida #0 \SelectBBC1
Sta parameter + 1
Lda #&7A
Ldx #parameter MOD 256
Ldy #parameter DIV 256
Jsr OSWORD
Rts
.parameter NOP:NOP
NEXT Pass
CALL SelectBBC1
The section below on Teletext OSWORD calls describes the calls available to 
you. Some entry points are used for internal Teletext filing-system operations 
and should not be called. Others are 'reserved for future expansion . . .'. 
Further information will be made available by Acorn in the form of a 
software applications note.


38 Using the Teletext system at assembly level
7.2 Teletext OSWORD calls
RELOAD PAGE
[&80]
The last page received must be re-fetched.
FETCH PAGE
[&85,p100,p10,p1,s1000,s100,s10,s1]
Request the page specified by the seven-digit page number given as the 
parameter. The sub-code is the time-code which is used for selecting a 
particular rolling page in a series of rolling pages. If any rolling page is 
acceptable, the sub-code digits should be set to &FF to denote that they are '
wild'. Page digits may also be set 'wild', and the page digits can be specified in 
either binary or ASCII hex. This call returns immediately. See TRANSFER for 
details of how to load a page into memory.
CHAINED PAGE
[&86]
Fetch the next page in the chain of pages of which the current page is part. The 
Telesoftware decoder uses this call to mean 'Get me the next block in the 
encoded Telesoftware file which I am loading sequentially'. If the current page 
is not part of a chain, the next rolling page to arrive is fetched instead.
HEAD OF CHAIN
[&88]
Follow the chain round until you find the page which is marked as being the 
head of the chain. The Telesoftware decoder uses this call to mean `Find me a 
page in which I can start looking for some encoded Telesoftware to decode' 
and also 'Get me the next block in the encoded Telesoftware file which I am 
loading in random order'. As with CHAINED PAGE, if the current page is not 
part of a chain, the next rolling page to arrive is fetched instead.
TEST ARRIVED
[&89, result]
Test to see if the last page requested has arrived.
Test succeeds:
result = &FF
Test fails:
result = 0
The page in question is LOCKED against further update if the test was 
successful.
UNLOCK PAGE
[&8A]
If the TEST ARRIVED command has shown that a page has been captured by 
the decoder, the page will have been locked against further


Using the Teletext system at assembly level 39
update. To secure updated versions of the page (or following pages in a 
series of rolling pages), the page must be UNLOCKED.
Note that reading data from a page using BGET on channel 15 also causes 
the page to be LOCKED.
SELECT CHANNEL
[&8B, channel]
Select channel 'channel' in the decoder hardware. Channel numbers should 
be given in the range 0 to 3 (binary or ASCII).
Note: This is different from Terminal mode, where the range 1 to 4 was 
chosen for the benefit of first-time users.
READ TSDP
[&8D, 16-bit address]
The readable part of the television service data packet (TSDP) is written to 
the area of store defined by the 16-bit address. As usual for the 6502, the 
address is passed in low, high' order. There is no interlock on this operation, 
as the packet is intended for direct display.
HAMMING DECODE
[&8E, encoded byte]
The 8-bit hamming-encoded byte is decoded, and the result returned in its 
place. A result of &FF means that an uncorrectable (more than 1 bit) error 
has occurred.
TRANSFER
[&8F, 32-bit address]
The current page is transferred to the address given. The address is 32 bits 
wide in order to allow data to be transferred to a site in the parasite processor.
The 32-bit address is stored in the form low, high, higher, highest'. The 
transfer waits if necessary until the page has been received. If this is not what 
you want, use the TEST ARRIVED call which lets you perform other 
operations while you are waiting. (This is the mechanism used by Terminal 
mode to poll for pages received.) TRANSFER automatically UNLOCKS a 
page after the data has been transferred.
HEADERS
[&92, 16-bit address]
The readable portion of all the headers being received will in future be 
written to the address given. This call is expected to be used for positioning 
the headers within the MODE 7 display.


40 Using the Teletext system at assembly level
WHAT CHANNEL
[&93, channel]
This call READS the currently selected channel number which it returns in the 
slot provided. As with SELECT CHANNEL, the result is in the range 0 to 3 (
binary).


8 Changing the filing
system
Your computer can have several filing systems available other than the 
Teletext system. The following commands are all used to exit from the current 
filing system into the one named.
*TAPE 3
300 baud cassette
*TAPE 12
1200 baud cassette
*TAPE
1200 baud cassette
*NET
Econet filing system
*TELE SOFT
The Telesoft mode of the Teletext system
*ROM
The cartridge ROM system
*DISC
The disc filing system
*DISK
Alternative spelling for above
Typing the command to enter the system you are already in has no effect. If 
you type the command to enter a filing system for which your computer is not 
equipped (ie you do not have the relevant filing system ROM) then the 
computer will respond with Bad command since it does not recognise the 
command.


9 Technical
information
This is mainly for interest and is not essential to using the Teletext Adapter. 
However, some of the material may prove useful if you wish to make full use 
of the Teletext system at assembler level. The information in this section 
covers the Teletext signals in general and the specific Tele software signals.
9.1 The structure and numbering of Teletext pages
A page can stand alone or be linked to another page to form a chain. Also, a 
number of stand-alone pages and/or chains can be accessed at a common level 
known as a branch. In this way a 'family tree' of pages can be formed with 
branching occurring at many levels. An example of this tree structure is given 
in Fig 5.1 which shows one way in which the contents of a newspaper could be 
transmitted. The first page contains the headlines and could be the index page 
with branching occurring at level 1 to four lead pages.
Lead 1 is the title page of a story covering four pages whilst lead 2 and lead 4 
are stand-alone single page items. Lead 3 could be a sub-index with branching 
occurring at level 2 to three separate stories.
The reason why Teletext uses such a structure is to enable you, by using 
simple commands, to find your way through the index/sub-index pages, 
branches and linked pages to the information item you wish to see.
Pages are numbered in groups of 100, called magazines, and a total of eight 
magazines are currently available for each broadcast channel although not 
every magazine and every page is necessarily transmitted. Each page is 
numbered with three digits, the first of which identifies the magazine it 
belongs to, and the second two the page number within that magazine. In 
addition, a further four digits are available for sub-page numbering, thus 
4070006 would be sub-page 0006 of page 07 in magazine 4.
Each magazine may have an index page which displays the magazine contents. 
This is usually the first page and is numbered 100, 200, 300 etc depending on 
the magazine.


Technical information 43
Page numbers are not normally reserved for specific items of information, so 
you must first display the index page to locate the correct page or sub-page 
number which can then be displayed.
If you select page 206, and page 210 is being transmitted at that instant, some 
time may elapse before the transmission sequence cycles back round to page 
206.
Index pages are, in fact, often transmitted at a faster rate than other data 
pages. This is to minimise the time you must wait before the selected index 
page is displayed. Another point which deserves mentioning is that not all 
pages are necessarily used. For example, it may be that in magazine 4, only 
pages 420 to 450 are transmitted.
Finally, there are rolling pages. These are pages which contain different 
information but are numbered the same as sub-pages, eg 0001, 0002 etc. A 
different rolling page is transmitted each time, which allows a great deal of 
information to be sent without changing the page number. For example, the 
BBC Newsreel is transmitted on page 199 but on every transmission a 
different rolling page is sent which contains different information (1990001, 
1990002, 1990003 etc). Suppose the rolling page was changed five times. 
This would give a series of five rolling pages numbered 1990001, 1990002, 
1990003, 1990004, 1990005.
As mentioned previously, Teletext pages are numbered by up to seven digits, 
made up as follows:
A one-digit magazine number in the range 0 to 7. A 
two-digit page number in the range 00 to 99.
A four-digit page sub-code in the range 0000 to 3979.
The magazine number is sent in the form of a single 3-bit binary number. 
The full range possible is thus 0 to 7 as used by the Teletext system.
The page number is sent in the form of two 4-bit binary numbers. This allows 
a range of 0 to 255, or 00 to FF hexadecimal, but at present the Teletext 
system only uses the range 0 to 99—the numbers being in binary coded 
decimal (BCD). Page numbers outside this range may be used for other 
purposes, as yet undefined.
The page sub-code is sent in the form of four binary numbers, whose lengths 
are given below:


44 Technical information
Most significant digit
— 2-bit binary number
Next digit
— 4-bit binary number
Next digit
— 3-bit binary number
Least significant digit
— 4-bit binary number
These binary numbers give a possible range of 8192 pages (0000 to 3F7F 
hexadecimal). At present, the Teletext system only uses sub-codes which have 
their 4-bit binary numbers lying in the range 0 to 9, and thus with the sub-code 
in the range 0000 to 3979. The use of 2- and 3-bit binary numbers explains the 
strange limits to the first and third digits.
The 2- and 3-bit binary numbers are a result of the fact that the last four digits 
were originally developed as a 'time code' and hence the full 0 to 9 range was 
not needed for these digits.
The Teletext specification does allow for hexadecimal page numbering with 
the full range of 0000000 to 7FF3F7F, but this is not used for conventional 
pages.
9.2 Teletext signals
A conventional Teletext decoder displays pages made up of 24 rows of 40 
characters per row (except for the first row — see below). The BBC 
Microcomputer Teletext System generates a 25th row for displaying system 
information, prompts etc. This 25th row displayed on the screen has nothing to 
do with the Teletext signals sent by the transmitter. The rest of this section 
deals with the general Teletext signals and the presence of this 25th row on the 
screen is ignored.
Teletext data is sent as a stream of digital bits forming 8-bit bytes. Each row 
consists of 45 bytes. All rows carry a row address or number in the range 0 to 
31. Rows 0 are the first row on any page and some of its 45 bytes are used to 
identify the page and to carry control information. This leaves 32 bytes for 
character codes. Rows 1 to 23 are the remaining 23 rows of 40 characters 
which, with row 0, make up the complete page. Rows 24 to 31 are often not 
transmitted. They are available to carry special information to the decoder.
The rows of 45 bytes are transmitted on the spare space between television 
picture fields. Four rows are currently sent between each picture field and a 
maximum of 16 is possible. The structure of the rows of bytes is discussed 
below.


Technical information 45
Rows 1 to 23
These 23 rows have a structure as shown in Fig 9.1.
Fig 9.1 Byte structure of Teletext rows 1 to 23
The first three bytes, the clock run-in (2 bytes) and framing code (1 byte) are 
used by the decoder for synchronising the row so that it can tell where one 
character byte ends and the next begins. The next two bytes, the magazine and 
row address bytes, give the magazine number (3 bits) and the row number or 
address (5 bits) arranged in such a way with the eight other bits to provide a 
means of error detection and correction. A discussion of the error protection is 
beyond the scope of this guide – it is dealt with in the reference given in 
section 9.4. The remaining 40 bytes are codes for the 40 characters which are 
to be displayed on corresponding rows on the television screen when the page 
is assembled. The codes are given in table 9.1.
Row
Rows with address or row number zero have a special status as page-headers. 
They are made up of 45 bytes like any other row, but only 32 bytes are 
available for character codes. The first 13 bytes are information bytes. The 
first five bytes carry the same information as for any other row, that is, the 
clock run-in, framing code, and magazine and row addresses. Bytes 6 and 7 
give the page number, units and tens respectively. Bytes 8 to 11 carry the sub-
code, the four least significant digits of the page number. Bytes 12 and 13 are 
a series of control bits to give information and instructions to the decoder 
about the page. The remaining 32 bytes are the character codes for display on 
row 0. All of the first 13 bytes are error protected as for the first five bytes of 
other rows.
When the Teletext decoder finds that it is receiving a row zero (by means of 
the information bytes at the start of the row) it interprets this as meaning that 
the previous row it received was the last one for the


46 Technical information
preceding page and that the current row it is receiving is the start of a new page 
for that magazine. Each row zero is thus used to determine the start and finish 
of the pages within a magazine. The rows sent between row zeros can be sent 
in any order (for example, row 1, row 15, row 9 ...) since they each have a row 
number or address amongst the first five bytes (see Fig 9.1). Several magazines 
may be transmitted simultaneously in unrelated order of rows. Blank rows need 
not be sent. If the decoder detects the completion of a page (by receiving the 
next page-header, row zero) it assumes that any row numbers not received for 
the previous page are blank rows.
To select a given page, the decoder examines the incoming rows of data until it 
finds a page-header with the correct page and magazine numbers. It then stores 
this row in its memory. The decoder continues to store each following row in 
the selected magazine until it receives the next page-header. It now has a 
complete page (bar blank rows) in memory and can decode the character codes 
to display the characters on the screen in the right places by making use of the 
row addresses.
Rows 24 to 31
These are often not transmitted but are available for sending special 
information to the decoder. In particular, row 27 is used to tell the decoder 
whether or not a page has any branch or chain linked pages connected with it. 
Rows 24 and 25 have the same structure as rows 1 to 23 and may be used so 
that a page can contain 1K or 1024 bytes of information. A normal page can 
only contain 32 + (23*40) = 952 bytes. The extra two rows provide another 80 
bytes which is sufficient to bring the total up to 1024 bytes without having to 
use all the 32 row zero bytes. In fact, eight of the row zero bytes are left free 
and these are currently used for the time information.
Page check word (row 27)
Row 27 includes a 16-bit cyclic redundancy check (CRC) on the first 24 
character bytes of row 0 and the 40 character bytes of rows 1-25 inclusive (a 
total of 1K bytes). For the purposes of this check word calculation any row not 
transmitted is assumed to carry 40 'space' bytes (hex 20).


Technical information 47
Table 9.1 Teletext character codes


48 Technical information
9.3 Character codes
Table 9.1 shows the available characters, their codes and also the control 
codes. These are the same characters which are available in mode 7 of the BBC 
Microcomputer — see chapter 28 of the User Guide for more details. The 
control codes can be sent in place of any character code anywhere in a row. 
The control codes are normally displayed as spaces (but see the section below 
on the hold graphics control). The fact that they can be used within a row 
enables one to change some aspect of the display part way through a row (for 
example, the display colour).
Display modes
There are three modes of display on the Teletext system — one alphanumeric 
mode and two graphics modes. The two graphics modes are called contiguous 
and separated. The difference is best shown by illustration, as in Fig 9.2.
Fig 9.2 Contiguous and separated graphics modes
Colour
Seven different display colours are provided (white, yellow, cyan, magenta, 
red, green and blue). Fourteen control codes are available to select 
alphanumerics or graphics and the required colour simultaneously. This 
enables a change of colour and mode in one step.
The background colour can be any of the seven colours listed above, or black. 
Coloured background is selected by using the 'new background' control code. 
After this code appears, the new background colour will be the display colour 
in use when the 'new background' control was used.


Technical information 49
Flashing and concealed characters
Two modes are provided in which the display characters appear as spaces 
some of the time. In flashing mode, a character appears alternately as a space 
and as the character at a rate determined by a clock in the computer. In 
conceal mode, the character appears as a space until revealed. The character is 
revealed by entering reveal mode which is done when the user issues the 
required command — such as the key f2 command in the Terminal mode of 
the BBC Microcomputer Teletext System.
Double height
Characters may be displayed at double height, in which case they take two 
rows. Thus the information sent in row n also applies to row n+1 in this mode. 
The decoder ignores row n+1 if it is sent.
Hold graphics control
The hold graphics control code allows a limited number of abrupt display 
colour changes. A control code is normally displayed as a space which thus 
causes a break in the display. In hold graphics mode, the character rectangle 
occupied by the control code is filled with a held graphics character. This can 
be used with any control code issued in the graphics mode. The held graphics 
character will be the most recent character with bit 6=1 in its code, provided 
that there has been no intervening change in either the alphanumeric/graphics 
modes or the normal/double height modes. In the absence of a suitable 
character, a space is displayed.
9.4 Reference
Broadcast Teletext Specification, Sept 1976
published jointly by
British Broadcasting Corporation
Independent Broadcasting Authority
British Radio Equipment Manufacturers' Association
9.5 The television service data packet
In addition to the above Teletext pages, a television service data packet is 
sometimes transmitted. If it is sent, it arrives once per second and carries the 
following information:


50 Technical information
1. An initial page address which a terminal should select at start-up without 
further user action. This will be the page selected by the BBC Microcomputer 
Teletext System at start-up. (In the absence of a television service data packet, 
page #00 is selected by default.) The contents of this page are controlled by 
the sender.
2. A program or network label.
3. An absolute time reference giving the time and date in a machine usable 
form.
4. A 20-character block of Teletext coded characters which are intended for 
direct display if the user requests a status report.
Byte structure of the television service data packet
The television service data packet (TSDP) is made up of 45 8-bit bytes. The 
first six bytes are for control, identification and synchronisation. The next 19 
bytes carry information in machine usable form. The last 20 bytes carry 
information for direct display when a status display is requested by the Teletext 
system.
In more detail, the 45 bytes are used as follows:
Bytes
Content
1- 2
Clock run-in
3
Framing code
4- 6
TSDP identification code
7-12
Default Teletext page
13-14
Channel identification
15
Time offset
16-18
Modified Julian date
19-21
Coordinated universal time (UTC)
22-25
Television program label
26-45
Status display message
Bytes 1 to 6 - decoder information
These six bytes provide information to enable the decoder to identify the TSDP 
as such and to synchronise the following bytes so that it can tell where one byte 
ends and the next begins.


Technical information 51
Bytes 7 to 12
These six bytes provide the Teletext decoder with the page number which it is 
to use to select a default page. These bytes are in machine readable form.
Bytes 13 and 14 - channel identification
These two bytes can be read by the machine to determine which channel is 
being received.
Byte 15 - time offset
This byte gives the offset in hours between the local clock time and the 
coordinated universal time (UTC). The first bit is always 1, the second bit gives 
the polarity of the offset. The last bit is also always 1. The other five bits are 
the offset. For example, the following offsets may be encountered in the UK:
During winter (GMT): 10000001 – no offset
During summer (BST): 10000101 – add one hour to UTC to get clock time
The five offset bits have the following weights: 8,4,2,1,1/2.
Bytes 16 to 18 - modified Julian date
These three bytes carry the modified Julian date which increments at UTC 
midnight. The first half byte is always 0101. The remaining two and a half 
bytes carry the date. Each 4-bit binary-coded-decimal number (half byte) is 
incremented by one before transmission. For example the three bytes may be:
55
5A
81
which would decode to 44970 or 1 January 1982.
The following notes should enable one to decode the modified Julian date to 
the standard format. BBC BASIC operators have been used.
Symbols:
JD – Julian date
Y – year from 1900
M – month (January = 1)
D – day of month
W – day of week (Sunday = 0, Monday = 1 etc)


52 Technical information
To find calendar date (in range 1/3/1900 to 28/2/2100):
Y1 = (100*(JD – 15078.2)) DIV 36525
M1 = INT((JD – 14956.1 – INT(365.25*Y))/30.6001)
D = JD – 14956 – INT(365.25*Y1) – INT(30.6*M1)
M = M1 – 1 – 12*K
Y = Y1 + K
where K = INT(0.7 + (1/(17 – M1))) ie IF M1 <14 K = 0 ELSE K = 1. To 
find day of week:
W = (JD+3) MOD 7
Bytes 19 to 21 - coordinated universal time
These three bytes give the time according to the UTC scale. Each 4-bit binary 
number in the group is incremented by one before transmission. The three 
bytes are hours, minutes and seconds respectively. For example:
1A 56 43
would decode to 09:45:32.
Bytes 26 to 45 - status display message
These 20 bytes carry the information which will be displayed when a status 
display is called for. A status display will occur after issuing the Terminal 
mode tune command SHIFT f4 .
9.6 The Telesoftware format
Names
This section deals with the format of the Telesoftware bytes which the 
Telesoftware decoder receives. The Telesoftware is sent as a string of 8-bit 
bytes in blocks of about 1000 bytes. The bytes actually sent are names of 
either individual program bytes or groups of bytes. Thus, before a program is 
sent by Telesoftware, all the characters, words etc are given a name. For 
example the word JSR used in a program might be given the name &45, while 
the letter 'A' might be given the name &C 1. All the names are single 8-bit 
bytes. At first thought it may appear that this means that only 256 names are 
available. However, this is doubled to 512


Technical information 53
distinct names by means of their classification into two types of names: lone-
names and escaped-names. The two types of name are told apart by the 
preceding byte sent. If the preceding byte is the name of the escape operator, 
then the name is an escaped-name. If the preceding byte is not the name of the 
escape operator then the name is a lone-name. For example, if the name of the 
escape operator is &1B, and a string of names received is:
&56
&89
&1B
&89
&67 . . .
the first two bytes are lone-names, the third byte is the name of the escape 
operator and so the fourth byte is an escaped-name. The fifth byte is a lone-
name.
When the Telesoftware decoder is first started up, it carries out an initialisation 
routine during which it sets up a table of names and their meanings in memory. 
The table set up contains the default meanings of the names. Entries in the 
table may be modified from time to time by incoming commands. The default 
table is given in table 9.2, the general Telesoftware table. The table set up by 
the BBC Microcomputer Teletext System will be somewhat different.
When the Telesoftware decoder is receiving Telesoftware, it looks up the 
names in the table and uses this to decode the Telesoftware.


54 Technical information
Table 9.2 (i) Name tables - default entries (&00 to &3F)
Value ASCII
Meanings
Value ASCII
Meanings
(hex) char
Lone
Escaped
(hex) char
Lone
Escaped
00
NUL
00
<ESC>
20
SP
20
<ESC>
01
SOH
01
<ESC>
21
!
21
<ESC>
02
STX
02
<ESC>
22
"
22
<ESC>
03
ETX
03
<ESC>
23
£
23
<ESC>
04
EOT
04
<ESC>
24
$
24
<ESC>
05
ENQ
05
<ESC>
25
%
25
<ESC>
06
ACK
06
<ESC>
26
&
26
<ESC>
07
BEL
07
<ESC>
27
'
27
<ESC>
08
BS
08
<ESC>
28
(
28
<ESC>
09
HT
09
<ESC>
29
)
29
<ESC>
0A
LF
0A
<ESC>
2A
*
2A
<ESC>
0B
VT
OB
<ESC>
2B
+
2B
<ESC>
0C
FF
OC
<ESC>
2C
,
2C
<ESC>
0D
CR
0D
<ESC>
2D
-
2D
<ESC>
0E
SO
0E
<ESC>
2E
.
2E
<ESC>
0F
SI
OF
<ESC>
2F
/
2F
<ESC>
10
DLE
10
<ESC>
30
0
30
<ESC>
11
DC1
11
<ESC>
31
1
31
<ESC>
12
DC2
12
<ESC>
32
2
32
<ESC>
13
DC3
13
<ESC>
33
3
33
<ESC>
14
DC4
14
<ESC>
34
4
34
<ESC>
15
NAK
15
<ESC>
35
5
35
<ESC>
16
SYN
16
<ESC>
36
6
36
<ESC>
17
ETB
17
<ESC>
37
7
37
<ESC>
18
CAN
18
<ESC>
38
8
38
<ESC>
19
EM
19
<ESC>
39
9
39
<ESC>
1A
SUB
1A
<ESC>
3A
:
3A
<ESC>
1B
ESC
<ESC>
1B
3B
;
3B
<ESC>
1C
FS
1C
<ESC>
3C
<
3C
<ESC>
1D
GS
1D
<ESC>
3D
=
3D
<ESC>
1E
RS
1E
<ESC>
3E
>
3E
<ESC>
1F
US
1F
<ESC>
3F
?
3F
<ESC>


Technical information 55
Table 9.2 (ii) Name tables - default entries (&40 to &7F)
Value ASCII
Meaning
Value ASCII
Meaning
(hex) char
Lone
Escaped
(hex) char
Lone
Escaped
40
@
40
<ESC>
60
-
60
<ESC>
41
A
41
<CET>
61
a
61
<DTL>
42
B
42
<TXT>
62
b
62
<DSB>
43
C
43
<TX8>
63
c
63
<DEB>
44
D
44
<VDX>
64
d
64
<DET>
45
E
45
<EMP>
65
e
65
<DSL>
46
F
46
<TXO>
66
f
66
<DSN>
47
G
47
<ESC>
67
g
67
<DNC>
48
H
48
<ESC>
68
h
68
<DST>
49
I
49
<ESC>
69
i
69
<DDT>
4A
J
4A
<ESC>
6A
j
6A
<DCO>
4B
K
4B
<ESC>
6B
k
6B
<DIG>
4C
L
4C
<ESC>
6C
1
6C
<DLA>
4D
M
4D
<ESC>
6D
m
6D
<DLR>
4E
N
4E
<ESC>
6E
n
6E
<DXA>
4F
0
4F
<ESC>
6F
o
6F
<DXR>
50
P
50
<ESC>
70
p
70
<DIR>
51
Q
51
<ESC>
71
q
71
<DES>
52
R
52
<ESC>
72
r
72
<DEC>
53
S
53
<ESC>
73
s
73
<DLS>
54
T
54
<ESC>
74
t
74
<DLC>
55
U
55
<ESC>
75
u
75
<DSA>
56
V
56
<ESC>
76
v
76
<DAC>
57
W
57
<ESC>
77
w
77
<ESC>
58
X
58
<ESC>
78
x
78
<DND>
59
Y
59
<ESC>
79
y
79
<DEF>
5A
Z
5A
<ESC>
7A
z
7A
<ESC>
5B
[
5B
<ESC>
7B
{
7B
<ESC>
5C
\
5C
<ESC>
7C
|
<ESC>
7C
5D
]
5D
<ESC>
7D
}
7D
<ESC>
5E
^
5E
<ESC>
7E
~
7E
<ESC>
5F
_
5F
<ESC>
7F
DEL
7F
<ESC>


56 Technical information
Table 9.2 (iii) Name tables - default entries (&80 to &BF)
Value ASCII
Meaning
Value ASCII
Meaning
(hex) char
Lone
Escaped
(hex) char
Lone
Escaped
80
NUL
80
<ESC>
A0
SP
A0
<ESC>
81
SOH
81
<ESC>
Al
!
Al
<ESC>
82
STX
82
<ESC>
A2
"
A2
<ESC>
83
ETX
83
<ESC>
A3
£
A3
<ESC>
84
EOT
84
<ESC>
A4
$
A4
<ESC>
85
ENQ
85
<ESC>
A5
%
A5
<ESC>
86
ACK
86
<ESC>
A6
&
A6
<ESC>
87
BEL
87
<ESC>
A7
'
A7
<ESC>
88
BS
88
<ESC>
A8
(
A8
<ESC>
89
HT
89
<ESC>
A9
)
A9
<ESC>
8A
LF
8A
<ESC>
AA
*
AA
<ESC>
8B
VT
8B
<ESC>
AB
+
AB
<ESC>
8C
FF
8C
<ESC>
AC
,
AC
<ESC>
8D
CR
8D
<ESC>
AD
-
AD
<ESC>
8E
SO
8E
<ESC>
AE
.
AE
<ESC>
8F
SI
8F
<ESC>
AF
/
AF
<ESC>
90
DLE
90
<ESC>
B0
0
B0
<ESC>
91
DC1
91
<ESC>
B1
1
B1
<ESC>
92
DC2
92
<ESC>
B2
2
B2
<ESC>
93
DC3
93
<ESC>
B3
3
B3
<ESC>
94
DC4
94
<ESC>
B4
4
B4
<ESC>
95
NAK
95
<ESC>
B5
5
B5
<ESC>
96
SYN
96
<ESC>
B6
6
B6
<ESC>
97
ETB
97
<ESC>
B7
7
B7
<ESC>
98
CAN
98
<ESC>
B8
8
B8
<ESC>
99
EM
99
<ESC>
B9
9
B9
<ESC>
9A
SUB
9A
<ESC>
BA
:
BA
<ESC>
9B
ESC
<ESC>
9B
BB
;
BB
<ESC>
9C
FS
9C
<ESC>
BC
<
BC
<ESC>
9D
GS
9D
<ESC>
BD
=
BD
<ESC>
9E
RS
9E
<ESC>
BE
>
BE
<ESC>
9F
US
9F
<ESC>
BF
?
BF
<ESC>


Technical information 57
Table 9.2 (iv) Name tables — default entries (&CO to &FF)
Value ASCII
Meaning
Value ASCII
Meaning
(hex) char
Lone
Escaped
(hex) char
Lone
Escaped
C0
51
C0
<ESC>
E0
-
E0
<ESC>
C1
A
C1
<CET>
E1
a
E1
<DTL>
C2
B
C2
<TXT>
E2
h
E2
<DSB>
C3
C
C3
<TX8>
E3
c
El
<DEB>
C4
D
C4
<VDX>
E4
d
E4
<DET>
C5
F
C5
<EMP>
E5
e
E5
<DSL>
C6
F
C6
<TXO>
E6
f
E6
<DSN>
C7
G
C7
<ESC>
E7
g
E7
<DNC>
C8
H
C8
<ESC>
E8
h
E8
<DST>
C9
I
C9
<ESC>
E9
i
E9
<DDT>
CA
J
CA
<ESC>
EA
j
EA
<DCO>
CB
K
CB
<ESC>
EB
k
EB
<DIG>
CC
L
CC
<ESC>
EC
1
EC
<DLA>
CD
M
CD
<ESC>
ED
m
ED
<DLR>
CE
N
CE
<ESC>
EE
n
EE
<DXA>
CF
0
CF
<ESC>
EF
o
EF
<DXR>
D0
P
D0
<ESC>
F0
p
F0
<DIR>
D1
Q
D1
<ESC>
F1
q
F1
<DES>
D2
R
D2
<ESC>
F2
r
F2
<DEC>
D3
S
D3
<ESC>
F3
s
F3
<DLS>
D4
T
D4
<ESC>
F4
t
F4
<DLC>
D5
U
D5
<ESC>
F5
u
F5
<DSA>
D6
V
D6
<ESC>
F6
v
F6
<DAC>
D7
W
D7
<ESC>
F7
w
F7
<ESC>
D8
X
D8
<ESC>
F8
x
F8
<DND>
D9
Y
D9
<ESC>
F9
y
F9
<DEF>
DA
Z
DA
<ESC>
FA
z
FA
<ESC>
DB
[
DB
<ESC>
FB
{
FB
<ESC>
DC
\
DC
<ESC>
FC
|
<ESC>
FC
DD
]
DD
<ESC>
FD
}
FD
<ESC>
DE
^
DE
<ESC>
FE
~
FE
<ESC>
DC
_
DF
<ESC>
FF
DEL
FF
<ESC>
Command subroutines
Looking at table 9.2, in the escaped-name meanings column you can see some as yet 
unexplained terms, eg escaped-name &41 corresponds to <CET>. These strings 
enclosed in angled brackets <> are names of command subroutines. The subroutines 
required by the Teletext Telesoftware decoder (as in the BBC Microcomputer decoder) 
are contained in the Teletext filing system ROM. Each command subroutine has a 
three-character code (eg <CET>). An instruction to the decoder appears in the form of 
the name of the relevant command subroutine to be executed, followed by the names of 
any operands required along with the number and size of the operands if this is not 
implied by the command subroutine.


58 Technical information
Each command subroutine has either a fixed (implied) number of operands or 
a variable number of operands. Each operand consists of either a fixed (
implied) number of decoded bytes or a variable number of decoded bytes. Any 
variable quantity (either number of operands or number of bytes in an 
operand) is preceded by a number giving its value on this occasion. For the 
Teletext system, this number is either a single decoded ASCII hexadecimal 
digit (' 0' to '9' and 'A' to 'F') or the decoded ASCII character 'X' followed by 
two decoded ASCII hexadecimal digits (most significant first). The general 
structure of a command before naming is:
<command subroutine>
<the number of operands, n, if variable>
<the number of names the first operand will encode to, i, if variable>
<the first operand>
<the number of names that the second operand will encode to, j>
<the second operand>
. . . and so on.
Many of the commands appearing in table 9.2 are not relevant to the Teletext 
system but are used by other systems making use of the general Telesoftware 
format. In general, there are three modes of obeying the commands — those 
which lie outside a block, those obeyed on the first pass and those obeyed on 
the second pass through the data. Any bytes received outside a block are 
ignored unless they are the names of the start block command and its 
operands, or a description of the medium being used. For the purposes of the 
first and second pass through the data, the block runs from after the start block 
command. Some commands are obeyed on the first pass through the block. If 
an end of block command is encountered, then the second pass stops at the 
name before this command. The rest of the commands are obeyed on the 
second pass through the block.
In the Teletext system, only one pass is made through the data, all the 
commands being obeyed on this pass.
A complete list of the commands relevant to the Teletext system along with a 
brief description is given in table 9.3. However, it should be noted that the 
table does not show all the commands listed in the name tables as not all of 
these are relevant to Teletext.


Technical information 59
Table 9.3 The command subroutines
Code
Command subroutine 
<DCO>
Comment
<DDT>
Define data type
<DEB>
End block
<DEC>
Change escaped-name's meaning (command)
<DEF>
Revert to default format
<DES>
Change escaped-name's meaning (decoded string)
<DET>
End of file
<DIG>
Ignore
<DIR>
Inhibit run
<DLA>
Load address (absolute)
<DLC>
Change lone-name's meaning (command)
<DLR>
Load address (relative)
<DLS>
Change lone-name's meaning (decoded string)
<DND>
No reversion to default format before next file
<DSB>
Start block
<DTL>
Title of file
<DXA>
Execution address (absolute)
<DXR>
Execution address (relative)
<ESC>
The escape operator
<TXT>
Teletext
<UER>
Error in transmission
<ULB>
Eight-bit byte adjustment (lower)
<URB>
Eight-bit byte adjustment (raise)
These commands relevant to the Teletext system are discussed below.
Start block and medium description commands
Start block <DSB>
Operands: 0, 1 or 2; each variable in length.
<DSB> marks the start of the block of data. The first operand is the number of 
this block. The second operand (which only needs to be present for one of the 
blocks of a file) is the number of blocks in the file. The blocks need not be 
numbered if the end of file <DET> command is used.
Example: <DSB> '1"2' '1' '0'
(This is the 16th block of the file.)


60 Technical information
Teletext <TXT>
Operands: 0, 1 or 2; each of variable length.
<TXT> makes the changes to the name table necessary for data with odd 
parity, streamlines the tables for Teletext and then executes the <DSB> 
subroutine to mark the start of the block.
Thus, any Telesoftware file for the BBC Microcomputer decoder received 
from CEEFAX will start with the name of this command.
The changes from the general format which are brought about are:
In the name tables, all names that would be a parity error if received are set 
to be names of the <UER>, error in transmission, subroutine. If they are 
received, the <UER> subroutine will alert the decoder that there has been a 
transmission error. All lone-names with correct parity are set to decode to 
themselves after a logical AND with &7F.
The command subroutine <ULB> is given the lone-name &E0 and the 
command subroutine <URB> is given the lone-name &FE. The escaped-
names &E0 and &FE are set to decode to themselves. The command 
subroutine <DSB> is given the escaped-name &42.
The decoder is set to expect numerical information (numbers describing 
variable operands, load addresses etc) to be given in ASCII hexadecimal 
digits.
Example: <TXT> '2"1"1"1"4'
(Teletext: This is the first block of four.)
End block <DEB>
Operands: none
<DEB> marks the end of a block of data. If the end of the block is marked by 
the end of a Teletext page then the <DEB> command is optional.
File and segment information commands
End of file <DET>
Operands: none
<DET> indicates that this block is the last block in a file. It can be omitted if 
the end of file is indicated by other means.


Technical information 61
Title of file <DTL>
Operands: 1, 2 or 3; each of variable length.
The operands of a <DTL> command describe the title of the Telesoftware file 
(first operand), its version number (optional second operand) and its date of 
issue (optional third operand). The date should be given as the modified Julian 
date (see section 9.5).
Files whose blocks may only be received in order are arranged on CEEFAX as 
a chain. The first block is marked as the chain-header and should contain a 
<DTL> command giving details of the file. Other blocks need not. Files whose 
blocks may be received out of order are also arranged on CEEFAX as a chain. 
However, each block is marked as a chain-header and should contain a <DTL> 
command.
Example: <DTL> '2"7"P"r"o"g"r"a"m"1"5'
(File title is 'Program'; version number 5.)
Comment <DCO>
Operands: variable number; each of variable length.
Comments are indicated by the <DCO> command, and may be displayed by 
the decoder whilst Telesoftware is decoded (the display is controlled in the 
BBC Microcomputer Teletext System by the Telesoft mode command *OPT1).
The recommended layout is:
1st operand – name of program
2nd operand – language
3rd operand – type of computer used
4th operand – date of publication
5th operand – source of program
6th operand – other comments
Example: <DCO> '1"9"A" "p"r"o"g"r"a"m'
(The name of the program is 'A program'.)
Ignore <DIG>
Operands: variable number; each of variable length.
The decoder will ignore the operands of a <DIG> command.


62 Technical information
Load address (absolute) <DLA>
Operands: 1 of variable length.
The operand of a <DLA> command is the first absolute address in memory 
that the decoded Telesoftware should be stored at (unless overruled when 
issuing the *LOAD command — see chapter 6 on the Telesoft mode).
The first decoded byte of the operand represents the most significant byte of 
the address.
Example: <DLA> '4"2"0' '0' '0'
(Store the Telesoftware starting at address &2000.)
Load address (relative) <DLR>
Operands: 0 or 1; of variable length.
The operand of a <DLR> command represents the offset from the first address 
that decoded Telesoftware is being stored at. Decoded Telesoftware should 
now be stored from this offset onwards.
The <DLR> command allows blocks to be received and decoded out of order.
If there is no operand, then the data should not be stored in a contiguous block 
of memory, but should be passed to a command line interpreter in whatever 
order the blocks are received and decoded. BASIC programs are loaded in this 
way after using the Telesoft mode command *EXEC.
Example: <DLR> '1"3"1' '0' '0'
(Store any further Telesoftware in memory starting at &2100— assuming that 
the base address is &2000).
Execution address (absolute) <DXA>
Operands: 1 of variable length.
The operand of a <DXA> command gives the execution address of the file of 
Tele software.
Example: <DXA> '4"2"0' 'F' '0'
(The execution address is &20F0.)
Execution address (relative) <DXR>
Operands: 1 of variable length.


Technical information 63
The operand of a <DXR> command gives the execution address relative to the 
load address of the file.
Example: <DXR> '2"F"0'
(The execution address is &20F0 — assuming that the base address is &2000.)
Inhibit run <DIR> 
Operands: none
The DIR command inhibits execution of the program immediately after its 
reception.
Define data type <DDT>
Operands: 1 or 2; of variable length.
The <DDT> command defines the type of data in the file and the hardware at 
which it is directed. The data type applies until superseded by a different 
<DDT> command.
Example: <DDT> '2"4"B"B"B"C"3"1"6"K'
(The following program is in BBC BASIC for a 16K machine.)
Format redefinition commands
Change escaped-name's meaning (decoded string) <DES>
Operands: 2; first of length 1 decoded byte, second of variable length.
The <DES> command changes the entry in the name tables for the escaped-
name given (first operand) to decode to the string given (second operand).
Example: <DES> 00 '4"w"o"r"d'
(The escaped-name 00 will decode to 'word')
Change escaped-name's meaning (command) <DEC>
Operands: 2; first of length 1 decoded byte, second of length 3 decoded bytes.
The <DEC> command changes the entry in the name tables for the escaped-
name given (first operand) to represent the command subroutine given (second 
operand).
Example: <DEC> FF 'U"E"R'


64 Technical information
(Reception of the escaped-name &FF indicates that there has been a 
transmission error – the command subroutine <UER> is executed.)
Change lone-name's meaning (decoded string) <DLS>
Operands: 2; first of length 1 decoded byte, second of variable length.
The <DLS> command changes the entry in the name tables for the lone-name 
given (first operand) to decode to the string of bytes given (second operand).
Example: <DLS> 00 '4"W"0"R"D'
(The lone-name 00 will decode to 'WORD')
Change lone-name's meaning (command) <DLC>
Operands: 2; first of length 1 decoded byte, second of length 3 decoded bytes.
The <DLC> command changes the entry in the name tables for the lone-name 
given (first operand) to represent the command subroutine given (second 
operand).
Example: <DLC> FF 'E"S"C'
(The lone-name &FF becomes a name of the escape operator.)
No reversion to default format before the next file <DND>
Operands: none
The <DND> command stops the decoder resetting its name tables to their 
default values prior to decoding the next file (see also the Telesoft mode call 
*OPT3).
Revert to default format <DEF>
<DEF> resets the name tables to their default values (see also the Telesoft 
mode call *OPT3).
The escape operator <ESC>
The function of the escape operator (<ESC>) is to indicate that an escaped-
name follows, rather than a lone-name. Thus it permits 512 distinct names 
rather than 256. The escape operator must have at least one lone-name and 
may have escaped-names.


Technical information 65
Eight-bit byte adjustment
For the Teletext system which only sends odd parity bytes, there are only 
effectively seven bits to the byte. The <ULB> and <URB> commands are 
available to 'add' an eighth bit.
Eight-bit byte adjustment (lower) <ULB>
Operands: 1 of decoded length 1 byte.
<ULB> indicates subtract &58 from the next decoded byte (to give a value in 
the range &C8 to &FF or &00 to &27, if only bytes in the range &20 to &7F 
can be transmitted).
Example: <ULB> 20
(Decodes to &C8.)
Eight-bit byte adjustment (raise) <URB>
Operands: 1 of decoded length 1 byte.
<URB> indicates add &58 to the next decoded byte (to give a value in the 
range &78 to &D7).
Example: <URB> 20
(Decodes to &78.)
Error in transmission <UER>
<UER> indicates that there has been an error in transmission.


Appendix 1
Installing the
TELEROM into the
BBC Microcomputer
CAUTION
STATIC SENSITIVE DEVICES — DO NOT HANDLE 
UNTIL YOU HAVE READ THESE INSTRUCTIONS
Please read these instructions carefully before attempting this conversion. If 
you are not completely confident of your ability to carry out this conversion 
yourself it will be in your own interests to take your unit to an authorised BBC 
Microcomputer dealer for him to carry out this upgrade.
First find out whether or not your computer has a series 1 operating system 
installed, by typing in *FX0 RETURN . If a number greater than 1.00 is 
displayed, you have a series 1 system.
1. Ensure that the computer is not connected to a mains power socket.
WARNING
DO NOT REMOVE THE LID OF THE COMPUTER 
WHILST IT IS CONNECTED TO THE MAINS
2. Unscrew the two large-headed screws on the rear panel of the computer and 
the two large-headed screws on the underside of the computer (near the front). 
Carefully remove the lid.
3. Unscrew the two (three on some computers) bolts securing the keyboard 
assembly to the lower case and carefully unplug the 17-way ribbon cable 
connecting the keyboard assembly to the main printed circuit board (PCB) by 
pulling the socket away from PL13 on the main PCB.
4. Move the keyboard away from the main PCB until the loudspeaker plug (
PL15) is accessible. Unplug the loudspeaker by carefully removing the socket 
from PL15. Place the keyboard assembly to one side on a flat surface.


Appendix 1 67
5. If your computer already contains a 'series 1' operating system then 
proceed to instruction 8.
6. The current Machine Operating System (MOS) is situated in the bottom 
right-hand corner of the main PCB in one of two configurations which are:
(i) One integrated circuit (IC) in socket IC51 identified by the legend 'B02' 
printed on the top. If you have this format carefully remove the MOS IC from 
IC51 using an IC extractor (a small screwdriver used with extreme care will 
do). Identify the BASIC language IC by the legend `B01' or 'B05' printed on 
it, and if it is not already in socket IC 101 then remove it as before and 
replace it in socket IC101 as described in '7' below.
(ii) Four ICs in sockets IC52, IC88, IC100 and IC101 (these sockets are all 
next to each other despite the numbering) identified with the legends 'C', 'D', '
E' and 'F' respectively printed on the top. If this is the case the BASIC 
language IC (identifiable by the legend 'B01' printed on the top and all four 
MOS ICs should be removed as described in (i) above. Replace the BASIC 
IC in socket IC 101 as described in '7' below.
7. The new MOS is supplied in a single IC identified by the legend 'B04' 
printed on the top. Insert the ROM carefully into the socket IC51 ensuring 
that all the 'legs' locate properly into the holes and are not 'bent under' upon 
insertion. The IC should be orientated so that the semicircular cutout in the 
top of the IC is at the top, ie away from the keyboard. Avoid touching the IC 
legs with your fingers wherever possible.
Now set the following links:
S18 North
S19 East
S20 North
S21 Two off east/west
S22 North
S32 West
S33 West
NB north is the edge of the PCB nearest to the back of the case and south is 
the edge nearest to the keyboard. East and west follow logically from these.


68 Appendix 1
8. Insert the TELEROM IC (identifiable by the legend 'TFS') into any free 
socket (IC88, IC100 or IC52) as described in '7' above.
Note: This User Guide assumes that the Teletext ROM is in the far right 
position of the filing system ICs (nearest the edge of the circuit board). If this 
is the case, then, when the microcomputer is powered up, the Telesoft filing 
system is automatically selected.
If the Teletext ROM is not in the far right position then the Telesoft filing 
system is not automatically selected on powering up. You can select Telesoft 
either by typing in
*TELESOFT RETURN
or by pressing the T and BREAK keys together.
9. Reassemble the BBC Microcomputer by reversing instructions 1 to 4 above. 
Your computer is now ready for use.


Appendix 2
Teletext reception
Teletext information is conveyed from the UHF TV transmitter to UHF 
domestic TV aerials as part of the complete 625 line UHF channel 
transmitted wave form. The pages of Teletext information are contained in a 
digitally coded form on unused blank lines which occur during the frame 
fly-back period and these pages of information are continually refreshed and 
updated. Thus a basic requirement for 'good' Teletext reception is 'good' TV 
reception, ie a 'clean' TV signal of adequate level.
Generally speaking 'good' Teletext reception should be possible in BBC/IBA 
defined UHF TV service areas with the usual 'line of sight' qualification, but 
may be difficult under fringe conditions.
A starting point is the reception of good quality, low noise (imperceptible 
snow), colour TV reception, but this alone will not guarantee error-free 
pages of Teletext information. Very close reflections of the received signal (
ghosting) can be almost imperceptible on a good colour picture but can still 
result in Teletext reception errors. This effect can vary between the four TV 
channels in use because the channels are of different frequencies and the 
reflections are usually frequency-dependent.
If problems are experienced a number of questions should be answered 
before condemning the equipment as faulty, or writing to the BBC/IBA 
and/or the equipment manufacturers etc:
1. Is the aerial of the correct group? (UHF bands are split into different 
groups throughout the country.) Reputable aerial manufacturers conform to 
specific technical standards which are essential for the best possible Teletext, 
and colour television, reception. The final display of Teletext information 
depends in the first instance on the aerial signal —this must be right before 
proceeding any further.
2. Was the aerial system properly installed externally with good quality UHF 
cable, avoiding kinks or sharp bends in the cable, and terminated in a good 
quality coaxial plug correctly fitted and soldered?
Note: Indoor aerials are not recommended for television or Teletext 
reception.


70 Appendix 2
3. Is the aerial of the correct polarisation (horizontal and vertical systems are 
employed in different regions of the UK) and is it directed towards the 
transmitter intended to serve the area? Out of area reception is often employed 
for a number of reasons, including ignorance of the correct transmitter for the 
area.
4. Will the aerial signals provide a good quality, low noise, colour television 
picture free from all reflections? (The new electronic test card is a valuable 
aid in detecting close reflections.)
If all of the above criteria are met it may be necessary to adjust the position of 
the aerial especially if Teletext character error rates vary between channels, or 
between pages of information.
The aerial should be tried in all positions, including variation of height, 
preferably by the use of the 'cranked arm' type of mast. If a satisfactory result 
is not possible by this means, moving the aerial to a different location is 
occasionally the only answer.
If the TV aerial signal is fed through amplifiers and/or signal splitting devices 
to feed more than one outlet, it may, in cases of Teletext reception difficulties, 
be necessary to feed the signal direct to the Teletext unit in the first instance. 
This will help to reduce any problems caused by the signal distribution 
system. If the Teletext unit is fed from a larger MATV (master aerial TV) 
system further professional advice should be sought from a reputable 
contractor.
Every effort should be made to ensure the best possible level and quality of 
signal so that the end result will not vary with time, weather conditions etc.
Expenditure on good quality aerial installations at the outset will prove to be 
an investment in the long term.


Appendix 3
Summary of Terminal
mode commands
The following is a quick reference list of all the Terminal mode commands 
together with the relevant keys, and the order in which they appear:
Description of command
Keys used
Select a channel
f4
Fine tune a channel
f4 and SHIFT
Select a page
f0
Select last explicit page
f1
Select index page
f1 and SHIFT
Keep a page
f3
Release a kept page
f3 and SHIFT
Reveal page
f2
Conceal page
f2 and SHIFT
Enter an operating system (*) command
f5
Save a page to file
f7
Load a page from file
f6
Hold page
f8
Exit to previous filing system
f9
Exit to Telesoft and execute
f9 and SHIFT








