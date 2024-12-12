import dotenv from "dotenv";
dotenv.config();

import { SensCritiqueGqlClient } from "senscritique-graphql-api";
import { gql } from 'graphql-request';

console.log(`Using SensCritique account: ${process.env.SC_EMAIL}`);

// Define the Product type
type UserInfos = {
  isWished: boolean;
  isDone?: boolean;
  isListed?: boolean;
};

type Product = {
  id: number;
  title: string;
  year_of_production: number;
  original_title?: string;
  rating?: number;
  release_date?: string;
  universe?: string;
  date_done?: string;
  myRating?: number;
  myWish?: boolean;
  targetRating?: number;
  targetWish?: boolean;
  userInfos?: UserInfos;
};

async function getSensCritiqueWishlist() {
  const client = await SensCritiqueGqlClient.build(process.env.SC_EMAIL!, process.env.SC_PASSWORD!);

  const query = gql`
    query {
      myWishes {
        id
        title
        year_of_production
        original_title
        rating
        release_date
        universe
        year_of_production
        date_done
        myRating
        myWish
        targetRating
        targetWish
        userInfos {
          isWished
          isDone
          isListed
        }
      }
    }
  `;

  // Fetch data from the API and cast it as an array of Product
  const data: { myWishes: Product[] } = await client.request(query);

  // Log the full response for debugging
  console.log("Full API Response from SensCritique:", JSON.stringify(data, null, 2));

  // Filter and analyze the data as needed
  const activeWishes = data.myWishes.filter((product) => product.userInfos?.isWished);
  console.log("Active Wishlist from SensCritique:", activeWishes);
}

getSensCritiqueWishlist();
