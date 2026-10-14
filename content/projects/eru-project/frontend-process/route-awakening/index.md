---
title: "03 - Route Awakening"
description: "The third phase of the eru frontend process."
date: 2026-05-06
weight: 3
showWordCount: true
showReadingTime: true
---

<div class="exam-portfolio-nav">
  <a class="exam-portfolio-nav__link" href="../">Overview</a>
  <a class="exam-portfolio-nav__link" href="../square-one/">01</a>
  <a class="exam-portfolio-nav__link" href="../react-set-go/">02</a>
  <a class="exam-portfolio-nav__link exam-portfolio-nav__link--current" href="../route-awakening/">03</a>
  <a class="exam-portfolio-nav__link" href="../beyond-the-frontend/">04</a>
</div>

## Overview

If all roads lead to Rome, then all routes lead through React Router.

So I guess we're just gonna step right into it. 
## Routes as the App Map

The route setup is in `routes.jsx`:

```jsx
<Routes>
  <Route path="/" element={<App />}>
    <Route element={<ProtectedRoute />}>
      <Route index element={<FeedPage />} />
      <Route path="feed" element={<FeedPage />} />
      <Route path="explore" element={<ExplorePage />} />
      <Route path="content/:contentId" element={<ContentDetailPage />} />
      <Route path="interactions" element={<InteractionsPage />} />

      <Route element={<ProtectedRoute requiredRole="ADMIN" />}>
        <Route path="admin" element={<AdminPage />} />
      </Route>
    </Route>

    <Route path="auth" element={<AuthPage />} />
    <Route path="auth/:mode" element={<AuthPage />} />
    <Route path="*" element={<NotFoundPage />} />
  </Route>
</Routes>
```

This file is the easiest way to explain the app structure.

```text
/auth/login        -> login
/auth/register     -> sign up
/feed              -> main feed
/explore           -> search/filter content
/content/:id       -> specific content item
/interactions      -> user activity
/admin             -> admin content management
```

So as we can see the auth routes are public and the rest of the app is wrapped in `ProtectedRoute`, because feed, explore, content details, interactions and admin should obviously not be open before login.

One thing I also had to remember is that SPA routing affects deployment. If a user refreshes `/content/12`, the server still has to return `index.html`, otherwise React Router never gets the chance to handle the route. That is why the Caddy setup needs the SPA fallback later, but we'll get to that. Hopefully.

## Protected Routes

`ProtectedRoute` is used around the routes that require login.

```jsx
function ProtectedRoute({ requiredRole }) {
  const outletContext = useOutletContext();
  const { currentUser } = outletContext;

  if (!currentUser) {
    return <Navigate to="/auth/login" replace />;
  }

  if (requiredRole && !currentUser.roles?.includes(requiredRole)) {
    return <Navigate to="/feed" replace />;
  }

  return <Outlet context={outletContext} />;
}
```

The first check handles normal protected pages. If there is no `currentUser`, the user is sent to login.

The second check is only used when a route has a role requirement. In eru, that is the admin route:

```jsx
<Route element={<ProtectedRoute requiredRole="ADMIN" />}>
  <Route path="admin" element={<AdminPage />} />
</Route>
```

I do not need a separate admin check inside `AdminPage`, because the route handles access before the page renders.

This is still only frontend access control. It keeps the navigation and UI clean, but the backend still has to check JWT and roles on the actual admin endpoints.

## Content Detail and Back Navigation

At first, content was mostly shown inside the feed. Later, I also needed to open content from explore and from the interaction overview.

Instead of duplicating the same content view in multiple places, I added one detail route:

```jsx
<Route path="content/:contentId" element={<ContentDetailPage />} />
```

The `:contentId` part is a route parameter. `ContentDetailPage` reads it like this:

```jsx
const { contentId } = useParams();
```

Then it loads the selected content and the user's interactions:

```jsx
Promise.all([
  eruApi.getContentById(contentId),
  eruApi.getMyInteractions(),
])
```

This made explore and interaction overview much simpler. They only need to link to `/content/${id}` instead of having their own detail logic.

But it also created a couple of small bugs.

One bug was the elaborate button. It worked in the feed, but not when content was opened from explore or interactions. The reason was that the feed had `explanation` and `elaborating` state inside `ContentViewer`, while the detail page did not have that state yet.

So `ContentDetailPage` was rendering the same `ContentCard`, but not giving it the same support around elaborate.

The fix was to add local state in `ContentDetailPage`:

```jsx
const [explanation, setExplanation] = useState("");
const [elaborating, setElaborating] = useState(false);
```

and pass it into the card:

```jsx
<ContentCard
  activeReactions={activeReactions}
  elaborating={elaborating}
  explanation={explanation}
  item={content}
  pendingReactions={pendingReactions}
  onElaborate={handleElaborate}
  onReact={handleReaction}
/>
```

That was a good example of a bug that was not about the component itself. `ContentCard` was fine. The parent page just did not provide the right state yet.

## Explore and Interaction Overview as Different Paths

Explore and interaction overview are both routes, but they solve different navigation problems.

The feed is more passive. The user sees one content item at a time.

Explore is more direct. The user can search and filter content:

```jsx
const [searchTerm, setSearchTerm] = useState("");
const [selectedAuthor, setSelectedAuthor] = useState("ALL");
const [selectedCategory, setSelectedCategory] = useState("ALL");
const [selectedType, setSelectedType] = useState("ALL");
```

Then a result can link to the detail page:

```jsx
to={`/content/${item.id}`}
```

Interaction overview does something similar, but from the user's own activity. If the user has liked, bookmarked, disliked or viewed something, the item can be opened again:

```jsx
<Link
  className="interaction-list-link"
  state={{ backLabel: "Back to Interactions", backTo: "/interactions" }}
  to={`/content/${contentId}`}
>
```

So the detail route becomes a shared destination.

That is cleaner than building separate detail displays inside explore and interactions. It also makes bug fixing easier, because the detail behavior lives in one page.

Search is handled client-side right now. The app loads content and filters the array in React. For the current amount of content, that is fine. If the project had thousands of content items, backend search and backend pagination would be better.

If I changed something here, I would probably put more filter state into the URL. Right now, explore search is local React state, so it resets on refresh. That is acceptable for this version, but query parameters would be better if users should share filtered views. 

## Final Thoughts on the Third Frontend Week

Think of it like this: if it wasn't for routing, we would all be staring endlessly at a *404 Page Not Found* screen for eternity.
But instead, we get sent to the content page, where countless interesting facts, theories, or quotes await.
Or even the explore page — where the possibilities are endless.

See you on the final page, where we will be looking at deployment!

<div class="exam-portfolio-pagination">
  <a role="button" href="../react-set-go/">Previous Chapter</a>
  <a role="button" href="../">Back To Overview</a>
  <a role="button" href="../beyond-the-frontend/">Next Chapter</a>
</div>
