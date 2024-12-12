import dotenv from "dotenv";
dotenv.config();

import { SensCritiqueGqlClient } from "senscritique-graphql-api";
import { GraphQLClient, gql } from 'graphql-request';
import { OperationTypeNode } from 'graphql';


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
