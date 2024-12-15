# PlexSync

This is a _WORK IN PROGRESS (WIP) as of 12th December 2024_

## Description

The tool aims to provide synchronization of watchlist, watch history and ratings between Plex and other services.

First aim will be to provide synchronization with SensCritique, communicating with its GraphQL API thanks to the work done on [senscritique-graphql-api](https://github.com/NitriKx/senscritique-graphql-api) by [NitriKx](https://github.com/NitriKx/) translated into Python since Plex's SDK is best in python than in TypeScript (I had started in TypeScript and gave up).

This is a side project and in active development.

## Glosary

- SC: [SensCritique](https://www.senscritique.com/)

## Current Features

- It can sync watchlists between Plex and SensCritique. Lots of challenges overcome over the week-end, could solve them with Postman Interceptor and ChatGPT help. I've never coded Python before so... yeah. Expect fuzzy stuff in the code.
- Sync works trough a persisted offline file which keeps track of items synced in both platforms, and whenever one gets removed to remove it in the other. Seems to work like a charm.

## Current Challenges

Create functions for ratings and for watched items, and synched them. Probably each on a different sync persisted file? Or maybe all in the same sync_data.json. Dunno.

## Goals

In order of priority

### Sync ratings

1. Create a function that gets every film/series/episode with a rating in Plex: recover it's id, it's title, year, type and rating.
1. Create a function that gets every film/series with a rating in SC: recover it's id, it's title, year, type and rating.
1. Create a function that puts each Plex rating into the corresponding SC item
1. Create a function that puts each SensCritique rating into the corresponding Plex item rating

1. Create a function that merges all ratings
   1. It gets all ratings from Plex and the rating date (or last watched date if not available)
   1. It gets all ratings from SC and the date of rating (or done_date if not available)
   1. Gets a list of films that are rated in both Plex and SC
   1. For each film in the list, it puts the latest rating in both platforms. Or else the lowest rating into the other one.

### Sync watched items

1. Create a function that gets every watched film/series/episode in Plex: recover it's watch_date, id, it's title, year, type and rating.
1. Create a function that gets every watched film/series/episode in SC: recover it's watch_date, id, it's title, year, type and rating.
1. Create a function that merges all watches
   1. It gets all watches from Plex and the watch date
   1. It gets all watches from SC and the watch date
   1. It makes sure both Plex and SC items are marked as watched at the latest of the two dates

## Contribute

If you want to contribute:

- Help me understand and document the GraphQL API, as most of its methods are obscure and have no related documentation eventhough the names are good leads
- Create the functions mentioned above to progress inside the project
- Write clean code (cf. [Clean Code Book](https://github.com/jnguyen095/clean-code/blob/master/Clean.Code.A.Handbook.of.Agile.Software.Craftsmanship.pdf))

## Before Running

1. **Clone the Repository**

   - Use the following command to clone the repository:

     ```bash
     git clone <repository_url>
     cd <repository_directory>
     ```

2. **Create an Environment File**

   - Create a file at the root of the repository named `.env` with the following content:

   ```plaintext

   # SensCritique
   PLEX_SERVER=your_plex_server_name
   PLEX_TOKEN=your_plex_api_token
   PLEX_USERNAME=your_plex_username
   PLEX_PASSWORD=your_plex_password

   # SensCritique
   SC_EMAIL=senscritiquemail@yourmail.com
   SC_PASSWORD=yoursenscritiquepassword
   SC_USER_ID=your-senscritique-userid
   ```

   - **Important**: This file is included in `.gitignore` to prevent accidental commits. Ensure that you do not commit this file to keep your Plex and SensCritique credentials safe.

3. **Install Dependencies**

   - Run the following command to install the required Python libraries:

     ```bash
     pip install -r requirements.txt
     ```

4. **Run or Deploy the Project**
   - Follow the instructions in the "Compiling & Deploying" section to run or deploy the project.

## Compiling & Deploying

Commands to run and deploy the project.

## Running Locally

1. **Install Dependencies**:
   - `pip install -r requirements.txt` - Installs required Python libraries.
2. **Run the Script**:
   - `python main.py` - Executes the project.

### Running Locally Using Docker

1. **Build Docker Image**:
   - `docker build -t plexsync .` - Builds the Docker image.
2. **Run Docker Container**:
   - `docker run --env-file .env -p 3000:3000 plexsync` - Deploys and runs the Docker container.

### Clean Recompiling After Errors

1. **Remove Cached/Generated Files**:
   - `rm -rf __pycache__` - Removes Python cache files.
   - `rm -rf dist` - Removes any previous build directory (if applicable).
2. **Rebuild Dependencies**:
   - `pip install -r requirements.txt` - Reinstalls all dependencies.
3. **Clean Docker Environment**:
   - `docker system prune -f` - Removes unused Docker images and containers.
4. **Rebuild Docker Image**:
   - `docker build -t plexsync .` - Rebuilds the Docker image.
5. **Run the Clean Docker Build**:
   - `docker run --env-file .env -p 3000:3000 plexsync` - Deploys and runs the clean build.

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
  const client = await SensCritiqueGqlClient.build(
    process.env.SC_EMAIL!,
    process.env.SC_PASSWORD!,
    {
      headers: {
        "Cache-Control": "no-cache",
      },
    }
  );

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
```

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
```

Was fixed by doing filtering on the isWished field

</details>
