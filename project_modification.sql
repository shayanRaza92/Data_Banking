DELETE FROM loan_payment;
DELETE FROM loan;
DELETE FROM archived_transaction;
DELETE FROM archived_account;
DELETE FROM [transaction];
DELETE FROM user_phone;
DELETE FROM account;
DELETE FROM rejected_user;

DELETE FROM [user]; 
DELETE FROM admin;

INSERT INTO admin (first_name, last_name, email, password, role) VALUES 
('Manager', 'One', 'manager@bank.com', 'admin123', 'Manager'),
('Accountant', 'Two', 'accountant@bank.com', 'admin123', 'Accountant');

INSERT INTO [user] (first_name, last_name, email, password, CNIC, Address_Street, Address_City, date_registered, Admin_ID)
VALUES ('Alice', 'Wonder', 'alice@example.com', 'pass123', '1111111111111', '123 Wonderland', 'Magic City', '2023-01-01', 1);

INSERT INTO [user] (first_name, last_name, email, password, CNIC, Address_Street, Address_City, date_registered, Admin_ID)
VALUES ('Bob', 'Builder', 'bob@example.com', 'pass123', '2222222222222', '456 Construction Rd', 'Build City', '2023-01-02', 1);

INSERT INTO [user] (first_name, last_name, email, password, CNIC, Address_Street, Address_City, date_registered, Admin_ID)
VALUES ('Charlie', 'Chaplin', 'charlie@example.com', 'pass123', '3333333333333', '789 Funny St', 'Laugh City', '2023-01-03', 1);

INSERT INTO [user] (first_name, last_name, email, password, CNIC, Address_Street, Address_City, date_registered, Admin_ID)
VALUES ('David', 'Copperfield', 'david@example.com', 'pass123', '4444444444444', '101 Magic Ln', 'Vegas', '2023-12-01', NULL);

INSERT INTO [user] (first_name, last_name, email, password, CNIC, Address_Street, Address_City, date_registered, Admin_ID)
VALUES ('Eve', 'Polastri', 'eve@example.com', 'pass123', '5555555555555', '202 Agent Way', 'London', '2023-01-05', 1);

INSERT INTO [user] (first_name, last_name, email, password, CNIC, Address_Street, Address_City, date_registered, Admin_ID)
VALUES ('Frank', 'Sinatra', 'frank@example.com', 'pass123', '6666666666666', '303 Blue Eyes', 'Hoboken', '2023-12-15', NULL);

INSERT INTO user_phone (user_id, phone) VALUES 
(1, '03001111111'),
(2, '03002222222'),
(3, '03003333333'),
(4, '03004444444'),
(5, '03005555555'),
(6, '03006666666');

INSERT INTO account (user_id, type, balance, date_created, status) VALUES (1, 'Normal', 50000, '2023-01-01', 'Active'); -- Acc 1
INSERT INTO account (user_id, type, balance, date_created, status) VALUES (1, 'Normal', 1000, '2023-01-01', 'Active');  -- Acc 2

INSERT INTO account (user_id, type, balance, date_created, status) VALUES (2, 'Normal', 5000, '2023-01-02', 'Active'); -- Acc 3

INSERT INTO account (user_id, type, balance, date_created, status) VALUES (2, 'Loan', 0, '2023-01-02', 'Active'); -- Acc 4 (Bob's Loan Acc)
INSERT INTO account (user_id, type, balance, date_created, status) VALUES (3, 'Loan', 0, '2023-01-03', 'Active'); -- Acc 5 (Charlie's Loan Acc)

INSERT INTO account (user_id, type, balance, date_created, status) VALUES (5, 'Normal', 0, '2023-01-05', 'Active'); -- Acc 6

INSERT INTO account (user_id, type, balance, date_created, status) VALUES (1, 'Loan', 0, '2023-01-01', 'Active'); -- Acc 7

INSERT INTO loan (account_number, admin_id, loan_amount, status, reason)
VALUES (4, 1, 100000, 'Approved', 'Home renovation'); -- Loan 1

INSERT INTO loan (account_number, admin_id, loan_amount, status, reason)
VALUES (5, NULL, 50000, 'Pending', 'Business expansion'); -- Loan 2

INSERT INTO loan (account_number, admin_id, loan_amount, status, reason)
VALUES (7, 1, 0, 'Paid', 'Car Loan'); -- Loan 3

INSERT INTO loan_payment (loan_id, payment_date, amount_paid) VALUES (3, '2023-06-01', 50000);

INSERT INTO [transaction] (account_number, amount, type, status, receiver_account, timestamp)
VALUES (1, 10000, 'Deposit', 'Approved', NULL, '2023-01-01');

INSERT INTO [transaction] (account_number, amount, type, status, receiver_account, timestamp)
VALUES (1, 500, 'Withdraw', 'Approved', NULL, '2023-03-01');

INSERT INTO [transaction] (account_number, receiver_account, amount, type, status, admin_id, timestamp)
VALUES (1, 3, 1000, 'Transfer', 'Approved', 1, '2023-06-01');

INSERT INTO [transaction] (account_number, amount, type, status, receiver_account, timestamp)
VALUES (1, 50000, 'Loan Payment', 'Approved', NULL, '2023-06-01');

INSERT INTO [transaction] (account_number, receiver_account, amount, type, status, admin_id, timestamp)
VALUES (1, 6, 500, 'Transfer', 'Pending', NULL, '2023-12-16');

INSERT INTO [transaction] (account_number, receiver_account, amount, type, status, admin_id, reason, timestamp)
VALUES (1, 3, 999999, 'Transfer', 'Rejected', 1, 'Insufficient Funds', '2023-07-01');

INSERT INTO rejected_user (original_user_id, first_name, last_name, email, CNIC, Address_Street, Address_City, date_registered, rejected_by_admin_id, rejection_reason, rejection_date)
VALUES (88, 'Bad', 'Guy', 'bad@example.com', '99999999999', 'Dark Alley', 'Gotham', '2023-01-01', 1, 'Fake details', '2023-01-02');

INSERT INTO archived_user (original_user_id, first_name, last_name, email, CNIC, Address_Street, Address_City, date_registered, deactivated_by_admin_id, deactivation_reason, deactivation_date)
VALUES (99, 'Ghost', 'User', 'ghost@example.com', '0000000000000', 'Graveyard', 'Silent Hill', '2022-01-01', 1, 'Requested deactivation', '2023-01-01');

INSERT INTO archived_account (original_account_number, user_id, type, balance, date_created) 
VALUES (9901, 99, 'Normal', 0, '2022-01-01');

INSERT INTO archived_transaction (original_trans_id, account_number, receiver_account, amount, type, timestamp, admin_id, status, reason)
VALUES (99001, 9901, NULL, 100, 'Deposit', '2022-06-01', NULL, 'Approved', '-');
