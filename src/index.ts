import dotenv from "dotenv";

import fetch from "node-fetch";
import { SensCritiqueGqlClient } from "senscritique-graphql-api";
import { gql } from "graphql-request";
import { XMLParser } from "fast-xml-parser";


type Media = {
  avatar: string;
  __typename: string;
};

type ProductMedia = {
  picture: string;
  __typename: string;
};

type Product = {
  id: number;
  genres: string[];
  medias: ProductMedia;
  year_of_production: number;
  release_date: string;
  title: string;
  myRating: number | null;
  myWish: boolean | null;
  targetWish: boolean | null;
  universe: string;
  __typename: string;
};

type User = {
  id: number;
  medias: Media;
  wishes: Product[];
  __typename: string;
};

type UserWishesResponse = {
  user: User;
};

type Me = {
  id: number;
  email: string;
  name: string;
  url: string;
};


dotenv.config();

console.log(`Using SensCritique account: ${process.env.SC_EMAIL}`);


async function fetchPlexWatchlist(): Promise<void> {
  const token = process.env.PLEX_TOKEN!;
  const endpoint = `https://metadata.provider.plex.tv/library/sections/watchlist/all?X-Plex-Token=${token}`;

  try {
    console.log("Fetching watchlist from Plex...");

    const response = await fetch(endpoint);
    if (!response.ok) {
      throw new Error(`Failed to fetch watchlist: ${response.statusText}`);
    }

    const xmlData = await response.text();

    // Configure the XML parser to parse attributes
    const parser = new XMLParser({
      ignoreAttributes: false, // Ensures attributes like `title` and `year` are preserved
      attributeNamePrefix: "", // Removes @ prefix from attribute keys
    });
    const jsonData = parser.parse(xmlData);

    const watchlist = jsonData.MediaContainer?.Video || [];
    if (watchlist.length === 0) {
      console.log("Your Plex watchlist is empty.");
    } else {
      console.log("\nPlex Watchlist:");
      watchlist.forEach((item: any) => {
        const title = item?.title || item?.title || "Unknown Title";
        const year = item?.year || item?.year || "Unknown Year";
        console.log(`- ${title} (${year})`);
      });
    }
  } catch (error) {
    console.error("Error fetching Plex watchlist:", error);
  }
}

// Fetch User Wishes from SensCritique
async function listUserWishes(): Promise<void> {
  const client = await SensCritiqueGqlClient.build(
    process.env.SC_EMAIL!,
    process.env.SC_PASSWORD!
  );

  const userWishesQuery = gql`
    query UserWishes(
      $avatarSize: String
      $id: Int!
      $universe: String
      $sortBy: String
      $limit: Int
      $offset: Int
      $pictureSize: String
    ) {
      user(id: $id) {
        id
        medias(avatarSize: $avatarSize) {
          avatar
          __typename
        }
        wishes(
          universe: $universe
          sortBy: $sortBy
          limit: $limit
          offset: $offset
        ) {
          id
          genres
          medias(pictureSize: $pictureSize) {
            picture
            __typename
          }
          year_of_production
          release_date
          title
          myRating
          myWish
          targetWish
          universe
          __typename
        }
        __typename
      }
    }
  `;

  const variables = {
    avatarSize: "30x30",
    id: 724296, // Replace with your actual user ID
    universe: "",
    sortBy: "user_last_action",
    limit: 30,
    offset: 0,
    pictureSize: "150",
  };

  try {
    const data = await client.request(userWishesQuery, variables);

    console.log(`User ID: ${data.user.id}`);
    console.log(`User Avatar: ${data.user.medias.avatar}`);
    console.log("Wishes:");
    data.user.wishes.forEach((wish: Product) => {
      console.log(`- ${wish.title} (${wish.year_of_production})`);
      console.log(`  Genres: ${wish.genres.join(", ")}`);
      console.log(`  Release Date: ${wish.release_date}`);
      console.log(`  Universe: ${wish.universe}`);
      console.log(`  Picture: ${wish.medias.picture}`);
    });
    
  } catch (error) {
    console.error("Error fetching user wishes:", error);
  }
}

/**
 * Adds a movie or series to the user's wishlist on SensCritique.
 * @param title - The title of the movie or series.
 * @param year - The release year of the movie or series.
 * @param type - The type: "movie" or "series".
 */
async function addToWishlist(title: string, year: number, type: "movie" | "series"): Promise<void> {
  const client = await SensCritiqueGqlClient.build(
    process.env.SC_EMAIL!,
    process.env.SC_PASSWORD!
  );

  // Step 1: Search for the movie/series by title and year
  const searchQuery = gql`
    query SearchMedia($query: String!, $mediaType: String, $year: Int) {
      search(query: $query, mediaType: $mediaType, year: $year) {
        items {
          id
          title
          year_of_production
          universe
          type
          medias {
            picture
          }
        }
      }
    }
  `;

  const searchVariables = {
    query: title,
    mediaType: type,
    year: year,
  };

  try {
    const searchResponse = await client.request(searchQuery, searchVariables);
    const items = searchResponse.search.items;

    if (items.length === 0) {
      console.log(`No ${type} found with title "${title}" and year "${year}".`);
      return;
    }

    const matchingItem = items[0]; // Assume the first match is the desired item
    console.log(`Found ${type}: "${matchingItem.title}" (${matchingItem.year_of_production})`);

    // Step 2: Add the movie/series to the wishlist
    const addToWishlistMutation = gql`
      mutation AddToWishlist($id: Int!) {
        addToWishlist(id: $id) {
          id
          title
          myWish
        }
      }
    `;

    const wishlistVariables = {
      id: matchingItem.id,
    };

    const wishlistResponse = await client.request(addToWishlistMutation, wishlistVariables);
    const addedItem = wishlistResponse.addToWishlist;

    if (addedItem.myWish) {
      console.log(`"${addedItem.title}" successfully added to your wishlist.`);
    } else {
      console.log(`Failed to add "${addedItem.title}" to your wishlist.`);
    }
  } catch (error) {
    console.error("Error adding to wishlist:", error);
  }
}

// Example Usage
(async () => {
  await addToWishlist("Amadeus", 1984, "movie");
})();

// // Run Both Functions
// (async () => {
//   console.log("\nFetching SensCritique User Wishes...\n");
//   await listUserWishes();
//   console.log("Fetching Plex and SensCritique data...\n");
//   await fetchPlexWatchlist();
// })();
