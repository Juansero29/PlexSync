# PlexSync

This is a _WORK IN PROGRESS (WIP) as of 12th December 2024_

## Description

The tool aims to provide synchronization of watchlist, watch history and ratings between Plex and other services.

First aim will be to provide synchronization with SensCritique, communicating with its GraphQL API thanks to the work done on [senscritique-graphql-api](https://github.com/NitriKx/senscritique-graphql-api) by [NitriKx](https://github.com/NitriKx/).

This is a side project and in active development so not currently working.

## Glosary

- SC: [SensCritique](https://www.senscritique.com/)

## Current Challenges

None. I am now able to retrieve all active items in the wish list of an user. I just need to get on with goal number one whenever I have the time.

## Goals

In order of priority

1. Create a function that allows to add a new movie/series into SC's wishlist
1. Create a function that allows to add a new movie/series into Plex's watchlist
1. Create a function that retrieves a movie/series inside Plex when searched by its title and release date, with its rating
1. Create a function that retrieves a movie/series inside SC when searched by its title and release date, with its rating
1. Create a function that allows to send all of the movies/series in Plex's watchlist into SC wishlist
1. Create a function that allows to send all of the movies/series in SC's wishlist into Plex
1. Create a function that synchronizes the wishes/watchlist between Plex and SC
   1. It should check that an item is not already in the list
   1. It should check that the two lists are identical at the end
      1. If lists are not identical, output the items that are missing and where they are missing
1. Create a function that gets every film/series with a rating in Plex
1. Create a function that gets every film/series with a rating in SC
1. Create a function that puts all Plex ratings into SC
1. Create a function that puts all SensCritique ratings into Plex
1. Create a function that merges all ratings
   1. It gets all ratings from Plex and the rating date (or last watched date if not available)
   1. It gets all ratings from SC and the date of rating (or last watched date if not available)
   1. Gets a list of films that are rated in both Plex and SC
   1. For each film in the list, it puts the latest rating in both platforms

## Contribute

If you want to contribute:

- Help me understand and document the GraphQL API, as most of its methods are obscure and have no related documentation even thoug the names are good leads
- Create the functions mentioned above to progress inside the project
- Write clean code (cf. [Clean Code Book](https://github.com/jnguyen095/clean-code/blob/master/Clean.Code.A.Handbook.of.Agile.Software.Craftsmanship.pdf))

## Before Compiling

1. Clone the repo
1. Create a file at the root of the repo named '.env' which has the following content

   ```raw
   SC_EMAIL=senscritiquemail@yourmail.com
   SC_PASSWORD=yoursenscritiquepassword
   PLEX_IP=your_plex_server_ip
   PLEX_TOKEN=your_plex_api_token
   ```

   This file is ignored since it's included .gitignore, be sure to not commit it to keep your Plex and SensCritique account safe

1. Now you can compile and deploy the project as described bellow

## Compiling & Deploying

Commands to compile the project

## Normal Compile

1. `npm run build` - Compiles npm
1. `node dist/index.js` - Deploys and runs

### Normal Compile using Docker

1. `npm run build` - Compiles npm
1. `docker build -t plexsync .` - compiles docker image
1. `docker run --env-file .env -p 3000:3000 plexsync` - deploys and runs docker image

### Clean recompiling after errors

1. `rd -r "dist"`
1. `npm run build`
1. `docker system prune -f`
1. `docker build -t plexsync .`
1. `docker run --env-file .env -p 3000:3000 plexsync`

## Overcome Challenges

### Wishlist retrieving wrong items

1. SensCritique seems to either cache info or have some latency in their GraphQL
   1. So recently added items into the Wishes are not returned by the API calls. This may need sometime to refresh and get returned by the API. I have added an item at 18h45 - 12/12/2024, and it's not returned immediately.
   1. I've made it so the function executes every 30 seconds until something is retrieved, I'll leave my PC on with the script running. We'll see at what time it will return something. Let's hope they don't ban me or detect me as a bot lol
   1. If new items in Wishes are never returned, then something is wrong with either my query or GraphSQL for SensCritique module => more tests to be done :/
   1. It's now 18h49 and nothing is returned yet.
1. Found another request in postman that allowed me to query for wishes of a specific user without having to authenticate.

### Wishlist not retrieving

~~As of now I'm focusing on extracting my own "Wishlist" from SensCritique via GraphQL, which is now partially working, since it succesfully authenticates with SensCritique and returns a list of movies that I have interacted with in the past, but that are not actually in my "Wishlist"~~

~~I'm trying to understand what "myWishes" query returns from the GraphQL API of SensCritique, which is not very clear to me as of now.~~

<details>
  <summary><del>Code</del></summary>

Old code causing trouble
```ts
    async function getSensCritiqueWishlist() {

        const client = await SensCritiqueGqlClient.build(process.env.SC_EMAIL!, process.env.SC_PASSWORD!, {
        headers: {
            'Cache-Control': 'no-cache',
        },
        });

    const query = gql`
        query {
        myWishes {
            id
            title
            year_of_production
        }
        }
    `;

    const data = await client.request(query);
    console.log("Wishlist from SensCritique:", data.myWishes);

    }

````

Current output:

```pwsh
Using SensCritique account: juansero29@gmail.com
Wishlist from SensCritique: [s\PlexSync>
  { id: 40631247, title: 'Severance', year_of_production: 2022 },
  { id: 7937926, title: 'Utopia', year_of_production: 2013 },
  { id: 43263904, title: 'The White Lotus', year_of_production: 2021 },
  { id: 42234, title: 'The Office (US)', year_of_production: 2005 },
  { id: 374603, title: 'Les Soprano', year_of_production: 1999 }
]
````

Was fixed by doing filtering on the isWished field

</details>
