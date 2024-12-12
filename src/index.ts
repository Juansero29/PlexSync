import * as dotenv from 'dotenv';
import { SensCritiqueGqlClient } from "senscritique-graphql-api";
import { gql } from "graphql-request";

dotenv.config();

console.log(`Using SensCritique account: ${process.env.SC_EMAIL}`);


async function getSensCritiqueWishlist() {
  const client = await SensCritiqueGqlClient.build(process.env.SC_EMAIL!, process.env.SC_PASSWORD!);

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

getSensCritiqueWishlist();
