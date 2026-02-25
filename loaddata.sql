-- -- Drop tables that have foreign keys first
-- DROP TABLE IF EXISTS "PostTags";
-- DROP TABLE IF EXISTS "PostReactions";
-- DROP TABLE IF EXISTS "Comments";
-- DROP TABLE IF EXISTS "Subscriptions";
-- DROP TABLE IF EXISTS "DemotionQueue";
-- DROP TABLE IF EXISTS "Posts";

-- -- Drop the parent tables last
-- DROP TABLE IF EXISTS "Tags";
-- DROP TABLE IF EXISTS "Reactions";
-- DROP TABLE IF EXISTS "Categories";
-- DROP TABLE IF EXISTS "Users";

CREATE TABLE "Users" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "first_name" varchar,
  "last_name" varchar,
  "email" varchar,
  "bio" varchar,
  "username" varchar,
  "password" varchar,
  "profile_image_url" varchar,
  "created_on" date,
  "active" bit
);

CREATE TABLE "DemotionQueue" (
  "action" varchar,
  "admin_id" INTEGER,
  "approver_one_id" INTEGER,
  FOREIGN KEY(`admin_id`) REFERENCES `Users`(`id`),
  FOREIGN KEY(`approver_one_id`) REFERENCES `Users`(`id`),
  PRIMARY KEY (action, admin_id, approver_one_id)
);


CREATE TABLE "Subscriptions" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "follower_id" INTEGER,
  "author_id" INTEGER,
  "created_on" date,
  FOREIGN KEY(`follower_id`) REFERENCES `Users`(`id`),
  FOREIGN KEY(`author_id`) REFERENCES `Users`(`id`)
);

CREATE TABLE "Posts" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "user_id" INTEGER,
  "category_id" INTEGER,
  "title" varchar,
  "publication_date" date,
  "image_url" varchar,
  "content" varchar,
  "approved" bit,
  FOREIGN KEY(`user_id`) REFERENCES `Users`(`id`)
);

CREATE TABLE "Comments" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "post_id" INTEGER,
  "author_id" INTEGER,
  "publication_date" date,
  "content" varchar,
  FOREIGN KEY(`post_id`) REFERENCES `Posts`(`id`),
  FOREIGN KEY(`author_id`) REFERENCES `Users`(`id`)
);

CREATE TABLE "Reactions" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "label" varchar,
  "image_url" varchar
);

CREATE TABLE "PostReactions" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "user_id" INTEGER,
  "reaction_id" INTEGER,
  "post_id" INTEGER,
  FOREIGN KEY(`user_id`) REFERENCES `Users`(`id`),
  FOREIGN KEY(`reaction_id`) REFERENCES `Reactions`(`id`),
  FOREIGN KEY(`post_id`) REFERENCES `Posts`(`id`)
);

CREATE TABLE "Tags" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "label" varchar
);

CREATE TABLE "PostTags" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "post_id" INTEGER,
  "tag_id" INTEGER,
  FOREIGN KEY(`post_id`) REFERENCES `Posts`(`id`),
  FOREIGN KEY(`tag_id`) REFERENCES `Tags`(`id`)
);

CREATE TABLE "Categories" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "label" varchar
);

INSERT INTO Categories ('label') VALUES ('News');
INSERT INTO Tags ('label') VALUES ('JavaScript');
INSERT INTO Reactions ('label', 'image_url') VALUES ('happy', 'https://pngtree.com/so/happy');
INSERT INTO Posts (user_id, category_id, title, publication_date, image_url, content, approved)
VALUES (1, 1, 'My First Post', '2024-02-14', 'https://example.com/image.jpg', 'This is the content of my post', 1);
SELECT * FROM Posts;

INSERT INTO Posts 
(user_id, category_id, title, publication_date, image_url, content, approved)
VALUES
(1, 1, 'Understanding React State', '2026-02-15',
 'https://example.com/react-state.jpg',
 'In this post, we explore how useState works and why state management is important in React applications.',
 1);

INSERT INTO Posts 
(user_id, category_id, title, publication_date, image_url, content, approved)
VALUES
(1, 2, 'Getting Started with REST APIs', '2026-02-15',
 'https://example.com/rest-api.jpg',
 'REST APIs allow communication between client and server using HTTP methods like GET, POST, PUT, and DELETE.',
 1);

INSERT INTO Posts 
(user_id, category_id, title, publication_date, image_url, content, approved)
VALUES
(2, 3, 'CSS Grid vs Flexbox', '2026-02-15',
 'https://example.com/css-layout.jpg',
 'Both CSS Grid and Flexbox are powerful layout systems. This article compares when to use each one.',
 0);

INSERT INTO Posts 
(user_id, category_id, title, publication_date, image_url, content, approved)
VALUES
(3, 4, 'Debugging Common JavaScript Errors', '2026-02-15',
 'https://example.com/js-debug.jpg',
 'Learn how to troubleshoot undefined variables, scope issues, and async bugs in JavaScript.',
 1);

INSERT INTO Posts 
(user_id, category_id, title, publication_date, image_url, content, approved)
VALUES
(4, 5, 'Building Your First Full-Stack App', '2026-02-15',
 'https://example.com/fullstack.jpg',
 'A step-by-step guide to building a full-stack application using React and a RESTful API.',
 0);

INSERT INTO Posts 
(user_id, category_id, title, publication_date, image_url, content, approved)
VALUES
(5, 6, 'Why Clean Code Matters', '2026-02-16',
 'https://example.com/clean-code.jpg',
 'Readable and maintainable code makes collaboration easier and reduces long-term technical debt.',
 1);

INSERT INTO Posts 
(user_id, category_id, title, publication_date, image_url, content, approved)
VALUES
(6, 7, 'Introduction to SQL Queries', '2026-02-16',
 'https://example.com/sql.jpg',
 'Learn how to write SELECT statements, filter results, and join tables in SQL.',
 1);

INSERT INTO Posts 
(user_id, category_id, title, publication_date, image_url, content, approved)
VALUES
(7, 8, 'Version Control with Git', '2026-02-16',
 'https://example.com/git.jpg',
 'Git helps track changes in your codebase and collaborate efficiently with other developers.',
 1);

INSERT INTO Posts 
(user_id, category_id, title, publication_date, image_url, content, approved)
VALUES
(8, 9, 'Preparing for Technical Interviews', '2026-02-16',
 'https://example.com/interview.jpg',
 'Practice coding problems, review data structures, and prepare behavioral answers to succeed in interviews.',
 0);

 INSERT INTO Categories ('label') VALUES ('Tech');
 INSERT INTO Categories ('label') VALUES ('Software');

INSERT INTO "Comments" ("post_id", "author_id", "publication_date", "content")
VALUES (1, 1, '2026-02-20', 'This is a great post! Thanks for sharing.');

INSERT INTO "Comments" ("post_id", "author_id", "publication_date", "content")
VALUES (1, 2, '2026-02-21', 'I disagree with the second paragraph, but overall good read.');

INSERT INTO "Comments" ("post_id", "author_id", "publication_date", "content")
VALUES (2, 1, '2026-02-22', 'Does anyone know if there will be a part 2 to this?');
