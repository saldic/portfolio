---
title: "02 - Laying the Foundation"
description: "Laying the foundation phase of the eru exam portfolio."
date: 2026-04-07
weight: 2
showWordCount: true
showReadingTime: true
---

<div class="exam-portfolio-nav">
  <a class="exam-portfolio-nav__link" href="../">Overview</a>
  <a class="exam-portfolio-nav__link" href="../planning-phase/">01</a>
  <a class="exam-portfolio-nav__link exam-portfolio-nav__link--current" href="../jpa-basics/">02</a>
  <a class="exam-portfolio-nav__link" href="../jpa-basics-and-relations/">03</a>
  <a class="exam-portfolio-nav__link" href="../data-integration/">04</a>
  <a class="exam-portfolio-nav__link" href="../rest-api/">05</a>
  <a class="exam-portfolio-nav__link" href="../rest-and-test/">06</a>
  <a class="exam-portfolio-nav__link" href="../security/">07</a>
  <a class="exam-portfolio-nav__link" href="../deployment/">08</a>
</div>

## Overview

Once the early project idea was settled, the next step was to set up the project structure. This week was therefore all about **laying the foundations** and getting the project to a point where it could actually **persist data** instead of just existing as an idea.

## Setting Up Hibernate

One of the most important classes in my setup at this stage was `HibernateConfig`, because it acted as the **main entry point** for the Hibernate configuration. It was the class the rest of the application called whenever it needed an `EntityManagerFactory`.

```java
public static EntityManagerFactory getEntityManagerFactory() {
    if (emf == null) {
        synchronized (HibernateConfig.class) {
            if (emf == null) {
                emf = HibernateEmfBuilder.build(buildProps());
            }
        }
    }
    return emf;
}
```

What this does is:

- ensure that the application only creates one `EntityManagerFactory`, which effectively makes it behave like a singleton throughout the application
- collect the Hibernate settings through `buildProps()`
- send those settings to `HibernateEmfBuilder`
- return the finished `EntityManagerFactory` to the rest of the application

Another important part of `HibernateConfig` is that it decides whether the application is running **locally** or in a **deployed environment**. In development, I used the `create` setting, which recreates the schema and clears the database on each run. That made it easier to test and work with the project using what I think of as a **“clean slate” principle**.

```java
private static Properties buildProps() {
    Properties props = HibernateBaseProperties.createBase();
    props.put("hibernate.hbm2ddl.auto", "create");

    if (System.getenv("DEPLOYED") != null) {
        setDeployedProperties(props);
    } else {
        setDevProperties(props);
    }
    return props;
}
```

This made the setup easier to reason about, because one class had the responsibility of:

- creating the base Hibernate configuration
- choosing the correct database settings
- preparing everything needed before Hibernate starts

I found this especially interesting because, for me, it was a **completely new way of working with databases**.

## Early Entity Design for Content

One of the first important entities was `Content`, because it represents the **actual educational material** that the whole platform revolves around:

```java
@Entity
@Table(name = "content")
public class Content {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;

    @Column(nullable = false)
    private String title;

    @Column(nullable = false)
    private String body;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
private ContentType contentType;
}
```

This was intentionally simple, but it already captured the basic domain idea:

- content has a title
- content has a body
- content has a type

What made this useful during the week was not just the class itself, but also the annotations around it. This was where I practiced the core JPA mapping concepts:

- `@Entity` to mark the class as persistent
- `@Table` to control the table mapping
- `@Id` and `@GeneratedValue` for the primary key
- `@Column` to define database column rules
- `@Enumerated` to persist enum values in a readable way, which I will return to later

## Understanding Hibernate and JPA

This was also the week where I got a much clearer understanding of the **difference between Hibernate and JPA**.

- **JPA** is the Java standard for persistence. It defines the annotations and APIs used to map Java objects to database tables.
- **Hibernate** is the framework that implements JPA and handles the actual ORM behavior in practice.

That distinction helped me understand why I was working with annotations such as `@Entity` and APIs such as `EntityManager`, while still relying on Hibernate to handle the actual database communication underneath. Since Hibernate builds on top of JDBC, it also meant I could work at a higher level of abstraction instead of writing raw JDBC code myself.

## The EntityManager

Another important part of the foundation phase was learning how **persistence actually happens in code**.

This was where `EntityManagerFactory` and `EntityManager` really started to make sense:

- `EntityManagerFactory` belongs to application startup and is expensive to create
- `EntityManager` is used for the actual unit of work against the database

Inside the DAO layer, I used `EntityManager` to perform CRUD operations. This also made transactions much more concrete, because writing data meant beginning a transaction, calling `persist` or `merge`, and committing it correctly.

## DAOs

I used a **DAO-based persistence layer** from the beginning instead of pushing database logic directly into controllers. That felt a little heavier at first, but it gave the project a **cleaner structure** later when services and tests were added.

One good example of that is `ContentDAO`, which became the place where all persistence logic for content was collected:

```java
public class ContentDAO implements IDAO<Content, Integer> {
    private final EntityManagerFactory emf;

    public ContentDAO() {
        this(HibernateConfig.getEntityManagerFactory());
    }
}
```

This was an important design choice because it meant controllers and services did not need to know how Hibernate worked internally. They only needed to call methods such as `create`, `getAll`, `getById`, `update`, or `delete`.

A small CRUD example from the DAO looks like this:

```java
public Content create(Content content) {
    try (EntityManager em = emf.createEntityManager()) {
        em.getTransaction().begin();
        em.persist(content);
        em.getTransaction().commit();
        return content;
    }
}
```

I think this class was useful for my understanding because it made the JPA flow very visible:

- create an `EntityManager`
- begin a transaction
- persist or merge the entity
- commit the transaction

## Content Type Enum

Another small but meaningful design choice was using an **enum for content type**:

```java
public enum ContentType {
    FACT,
    THEORY,
    QUOTE;
}
```

This helped me avoid using random strings throughout the codebase. Instead of storing a free-text type everywhere, I had a limited set of valid values that matched the domain more clearly.

That enum was then used directly in the `Content` entity:

```java
@Enumerated(EnumType.STRING)
@Column(nullable = false)
private ContentType contentType;
```

This was a nice design decision for two reasons:

- it made the model more type-safe in Java
- it stored the enum as readable text in the database instead of as unclear numeric values

So `ContentDAO` and `ContentType` may look small on their own, but together they show two of the core backend ideas from this phase:

- persistence logic should be separated into dedicated classes
- domain rules should be represented as clearly as possible in the model

## JPA Lifecycle States

![JPA lifecycle states and the Goblin Banker](/images/GoblinBanker.png)

*Screenshot from Jon Bertelsen's teaching video "03-jpa-basics-entity-lifecycle", taken by the author.*

This diagram shows the four lifecycle states of a JPA entity and how the `EntityManager` aka `Goblin Banker` controls them and delegates these different states to them.

- **Transient** means the object exists only in Java and is not yet managed or stored in the database.
- **Managed** means the object is tracked by the `EntityManager`, so changes to it can be synchronized with the database.
- **Detached** means the object was previously managed, but is no longer being tracked.
- **Removed** means the object has been marked for deletion and will be deleted from the database on flush or commit.

The diagram helped me understand that JPA does not just save objects directly. Instead, entities move between different states depending on methods such as `persist()`, `find()`, `merge()`, and `remove()`.

## Final Thoughts on the Second Week

This week was where the project started to **feel real**. The idea was no longer just something conceptual, because I now had the **basic persistence layer**, **Hibernate configuration**, and the **first entities** in place.

What made this week especially important for me was that I was not just writing code to make something work, but also starting to understand the architectural reasoning behind it. Setting up `HibernateConfig`, working with `EntityManagerFactory` and `EntityManager`, and introducing a DAO layer gave me a much clearer picture of how persistence is structured in a Java backend application.

<div class="exam-portfolio-pagination">
  <a role="button" href="../planning-phase/">Previous Chapter</a>
  <a role="button" href="../jpa-basics-and-relations/">Next Chapter</a>
</div>
