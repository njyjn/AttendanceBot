# AttendanceBot
I am a Telegram bot which helps Caregroup Leaders in Arrow Ministry automatically tabulate their group attendance.

- [User Guide](#getting-started-for-users)
- [Admin Guide](#getting-started-for-admins)
- [Developer Guide](#getting-started-for-developers)

## Getting started for users

**Hello, I am Arrow CGL Bot (ACGLBOT)!**

I help you take attendance for Arrow events so that you can spend more time on what is truly important—your youths. Say goodbye to that copy/pasting/calculating race-to-not-be-last (my creator was always last).

I am so simple to use! To begin, enter `/start Your Name CG`. For example, if my name is **Alethea Sim** and I am from **TJC** (which is the best CG by the way), enter `/start Alethea Sim TJ`. Your CG's code may not be what you think it is. Check `/cg` to tell me the code that I can understand.

Your Cluster Rep (CR) will approve your registration. If you do not receive an approval message within a minute, your CR may be swamped with friend requests at the moment... Try again! If you are ever asked for your 'chat id', hit `/24601` and give them the string of numbers. No, you aren't Jean Valjean unless your chat id is really 24601 to which inform @njyjn immediately.

When an Arrow event is taking place, you will receive a notifcation asking you to 'get /count-ing'. Yes! Do exactly that. Hit `/count` and follow the steps to the end.

If you need to make changes to your attendance, repeat `/count`. Complete the steps to the end; do not leave me hanging or your CG's data may be corrupted.

You will be notified if you are the last CG to submit attendance. To which I say to you, very good! You will have to copy and paste it into the **JC Updates** WhatsApp chat. Just so you know, WhatsApp and I aren't very good friends. In the future we won't even have to talk to it and I will let Pastor and our overseers know directly! Yay!

You may also talk to me if I am free, but I am a bot who does not understand the full range of your language. I will try my best to reply you. No more blue ticks and conversations leaving you wondering why you started it in the first place, ok?

Anytime that you have had it with me, you may click `/stop`, but that deregisters you from the system and your CR will have to add you in again when you hit `/start`. Let's save them the hassle and remain subscribed to me for as long as you are serving in Arrow.

If you have any questions, feedback or suggestions, do let my creator know on Telegram at @njyjn. God bless you :-)

## Getting started for admins
Only cluster reps and above receive administratorship over ACGLBOT. Currently, they are

| Cluster | Rep |
|---|---|
| East | Choy (the handsome one)|
| North | TBC |
| South | Sherry |
| West United | TBC |
| West ACIB | TBC |

As an administrator you are the gatekeeper to a number of things:

### User management
#### Registration 
When a leader under your care registers, you will receive a message seeking your approval. A custom keyboard with a single button will appear, and all you have to do is to click on it. 

In the event that multiple people are registering at the same time, the keyboard button may change and will not return to the previous user. So ask your leaders to take it slowly, k, slowly!

You may add them manually too. Use `/add cg chatID Name` using the `cg` code found in `/cg`, their `chatID` which is obtained when they enter `/24601`, and their `Name` which really is just their name and nothing more. Note the spaces which separate the parameters.

It is your onus to ensure that only your leaders register on the bot.

#### Removal
When a leader leaves your care, you have to inform the superadmin (@njyjn as of now) to remove them from the system. Or they could just hit `/stop`

#### List
You would know this if you have toyed with Unix systems before. You can retrieve a list of leaders under your care by hitting `/ls`. To list all users listening to me, hit `/ls la`. Otherwise, `/ls cg` where `cg` is the code I understand. (Check `/cg` if you are unsure)

### Event management 
You are able to create events that kickoff attendance taking. Note that only one event may run at any given time, and all events automatically expire and self-destruct within 3 days.

Attendance data is only stored within the aforementioned timeframe. We recommend that the practice of storing the final count in a safe place continues.

#### Create
`/event new Name of event` gets you started. Do this only once or I may whine!

#### Report
`/event report` tells you the state of the count at the time you requested for it. In future iterations you will be automatically notified when the entire cluster has completed its attendance taking.

#### End
`/event end` ends the current counting event. Please do this only when the attendance taking is complete. Data is safe and you may reopen it within 3 days from the start.

#### Reopen
`/event reopen` reopens the previous counting event, provided it has yet to self-destruct.

#### Clear
`/event clear` removes data from the system. WARNING: You may not retrieve cleared attendance data.

### Communications
`/yell Your message here` sends 'Your message here' to all listening users. Use only if important.

## Getting started for developers
Refer to [Developer Guide](/Developer.md).

---

## Contributors

* **Nick Lee** - *Telepot* - [nickoala](https://github.com/nickoala/telepot)
* **Darren Wee** - *Code Base* - [darrenwee](https://github.com/darrenwee)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

