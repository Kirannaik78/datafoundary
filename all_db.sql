create database email_db
use email_db
create table emails (
    id varchar(255) primary key,
    from_email varchar(255),
    subject TEXT,
    body TEXT,
    received_datetime DATETIME,
    is_read BOOLEAN default False,
    folder varchar(50) default 'Inbox'
)