import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import HomepageFeatures from '@site/src/components/HomepageFeatures';

import Heading from '@theme/Heading';
import styles from './index.module.css';

function HomepageHeader() {
  const { siteConfig } = useDocusaurusContext();
  return (
    <header className={clsx("hero hero--primary", styles.heroBanner)}>
      <div className="container">
        <Heading as="h1" className="hero__title">
          {siteConfig.title}
        </Heading>
        <p className="hero__subtitle">{siteConfig.tagline}</p>
        <div className={styles.buttons}>
          <Link
            className="button button--secondary button--lg"
            to="/docs/introduction"
          >
            Anaya🔥 Doc📑 - 5min ⏱️
          </Link>
        </div>
        <div className={styles.gap}>
          <Link
            className="button button--secondary button--lg"
            to="https://github.com/swax10/anaya"
          >
            GitHub🔗
          </Link>
        </div>
      </div>
    </header>
  );
}

export default function Home() {
  const { siteConfig } = useDocusaurusContext();
  return (
    <Layout
      title={`${siteConfig.title}`}
      description="Anaya🔥📑: The Multimodal Retrieval-Augmented Generation Content Engine"
    >
      <HomepageHeader />
      <main>
        <p className={styles.projectDescription}>
          Anaya🔥📑: <br></br>
          The Multimodal Retrieval-Augmented Generation Content Engine. With the
          ability to analyze multiple PDFs as input and harness their knowledge
          base, Anaya generates insightful and comprehensive outputs,
          revolutionizing the way information is retrieved and presented.
        </p>
        <HomepageFeatures />
      </main>
    </Layout>
  );
}
