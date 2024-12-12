import dotenv from "dotenv";
dotenv.config();

import { SensCritiqueGqlClient } from "senscritique-graphql-api";
import { gql } from "graphql-request";

console.log(`Using SensCritique account: ${process.env.SC_EMAIL}`);

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
    const currentTime = new Date().toLocaleString();
    const data: UserWishesResponse = await client.request(userWishesQuery, variables);

    // console.log(`[${currentTime}] User Wishes Response:`, JSON.stringify(data, null, 2));

    // Example of structured display:
    console.log(`User ID: ${data.user.id}`);
    console.log(`User Avatar: ${data.user.medias.avatar}`);
    console.log("Wishes:");
    data.user.wishes.forEach((wish) => {
      console.log(`- ${wish.title} (${wish.year_of_production})`);
      console.log(`  Genres: ${wish.genres.join(", ")}`);
      console.log(`  Release Date: ${wish.release_date}`);
      console.log(`  Universe: ${wish.universe}`);
      console.log(`  Picture: ${wish.medias.picture}`);
    });
  } catch (error) {
    const currentTime = new Date().toLocaleString();
    console.error(`[${currentTime}] Error fetching user wishes:`, error);
  }
}


// Call both functions to demonstrate both "me" and "List Wishes"
listUserWishes();
