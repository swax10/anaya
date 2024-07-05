import clsx from "clsx";
import Heading from "@theme/Heading";
import styles from "./styles.module.css";

const FeatureList = [
  {
    title: "Innovative Approach",
    description: (
      <>
        Anaya represents a leap forward in content generation, leveraging
        advanced retrieval-augmented techniques to revolutionize information
        processing.
      </>
    ),
  },
  {
    title: "Multi-PDF Analysis",
    description: (
      <>
        With the unique capability to analyze multiple PDFs, Anaya harnesses a
        vast knowledge base, ensuring rich and informed content generation.
      </>
    ),
  },
  {
    title: "Comprehensive Outputs",
    description: (
      <>
        Anaya's outputs are not only insightful but also comprehensive, making
        it an invaluable tool for presenting information in a clear and
        accessible manner.
      </>
    ),
  },
];

function Feature({title, description }) {
  return (
    <div className={clsx("col col--4")}>
      <div className="text--center padding-horiz--md">
        <Heading as="h3">{title}</Heading>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures() {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
