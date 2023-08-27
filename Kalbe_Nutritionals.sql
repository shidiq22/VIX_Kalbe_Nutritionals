--1. What is the average age of customers based on their marital status?
SELECT marital_status, round(avg(age)) average_age FROM customer
GROUP BY marital_status ORDER BY marital_status ASC;

--2. What is the average age of customers based on their gender?
SELECT gender, round(avg(age)) average_age FROM customer
GROUP BY gender ORDER BY gender ASC;

--3. Determine the store name with the highest total quantity!
SELECT storename, sum(qty) sum_qty FROM transaction t
INNER JOIN store s ON t.storeid = s.storeid
GROUP BY storename ORDER BY sum_qty DESC LIMIT 1;

--4. Identify the best-selling product by total amount!
SELECT product_name, sum(totalamount) sum_totalamount FROM transaction t
INNER JOIN product p ON t.productid = p.productid
GROUP BY product_name ORDER BY sum_totalamount DESC LIMIT 1;