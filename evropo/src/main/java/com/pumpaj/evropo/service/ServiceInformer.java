package com.pumpaj.evropo.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.pumpaj.evropo.model.ModelInformer;
import com.pumpaj.evropo.repository.RepositoryInformer;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.data.mongodb.core.MongoTemplate;
import org.springframework.data.mongodb.core.query.Criteria;
import org.springframework.data.mongodb.core.query.Query;
import org.springframework.core.io.ClassPathResource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.*;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.util.*;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

@Service
public class ServiceInformer {

    private static final Logger logger = LoggerFactory.getLogger(ServiceInformer.class);

    @Autowired
    private RepositoryInformer repository;

    @Autowired
    private MongoTemplate mongoTemplate;

    @Value("${python.script.path.informer:scripts/scraper_informer_najnovije.py}")
    private String scriptPath;

    @Value("${python.executable.path:python}")
    private String pythonPath;

    // Keywords and their variations in Serbian
    private static final List<String> KEYWORDS = Arrays.asList(
            // protest variations
            "protest", "protesta", "proteste", "protestu", "protestima", "protesti", "protestni", "protestna", "protestno",
            // blokada variations
            "blokad", "blokade", "blokadu", "blokadom", "blokadama", "blokira", "blokiraj", "blokirano",
            // student variations
            "student", "studenti", "studenta", "studente", "studentu", "studentski", "studentska", "studentsko", "studiraju",
            // šetnja variations
            "šetnja", "šetnje", "šetnju", "šetnjom", "šetnjama", "šetn", "šeta", "hod", "marš", "demonstrac",
            // javni čas variations
            "javni", "čas", "cas", "javnog", "javnom", "časa", "casa", "javnoj", "časov", "casov",
            // additional related terms
            "skupština", "skup", "okupljanje", "okupio", "okupila", "okupili", "okupljaj", "protest", "demonstrant",
            // profesor
            "profesor", "profesoru", "profesori", "profesorski", "profesorsku", "profesorske", "profesora", "profesorom", "profesorka",
            // informer kancer
            "blokaderi", "blokaderski", "ustaše", "boljševici", "plenum", "plenumaši", "blokaderska", "blokadera", "plenumaša", "plenumašu", "blokaderu", "obojena", "revolucija", "obojenu", "revoluciju", "obojene", "revolucije"
    );

    public List<ModelInformer> getViableLinks() {
        logger.info("Getting viable links from informer.rs");

        // 1. Run Python script to get links
        List<Map<String, String>> scrapedLinks = runPythonScraper();

        // 2. Save or update links in MongoDB
        saveScrapedLinks(scrapedLinks);

        // 3. Find unvisited links that match keywords
        List<ModelInformer> viableLinks = findUnvisitedWithKeywords();

        logger.info("Found {} viable links", viableLinks.size());
        return viableLinks;
    }

    private List<Map<String, String>> runPythonScraper() {
        List<Map<String, String>> articles = new ArrayList<>();
        ObjectMapper objectMapper = new ObjectMapper();

        try {
            // Extract script from classpath to temporary location
            File tempScript = extractScriptFromClasspath();

            // Build the command
            List<String> command = Arrays.asList(pythonPath, tempScript.getAbsolutePath());

            ProcessBuilder pb = new ProcessBuilder(command);
            pb.redirectErrorStream(true);
            Process process = pb.start();

            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
            String line;

            // Read output
            while ((line = reader.readLine()) != null) {
                logger.info("Python script output: {}", line);

                // Try to parse as JSON
                if (line.startsWith("{")) {
                    try {
                        @SuppressWarnings("unchecked")
                        Map<String, String> article = objectMapper.readValue(line, Map.class);
                        if (article.containsKey("title") && article.containsKey("link")) {
                            articles.add(article);
                            markAsVisitedUsingLink(article.get("link"));
                        }
                    } catch (Exception e) {
                        logger.debug("Failed to parse JSON: {}", line);
                    }
                }
            }

            process.waitFor();

            // Clean up temporary file
            tempScript.delete();

        } catch (Exception e) {
            logger.error("Error running Python scraper: ", e);
        }

        return articles;
    }

    private File extractScriptFromClasspath() throws IOException {
        ClassPathResource resource = new ClassPathResource(scriptPath);

        // Create a temporary file
        File tempFile = File.createTempFile("scraper", ".py");
        tempFile.deleteOnExit();

        // Copy the resource to the temporary file
        try (InputStream is = resource.getInputStream()) {
            Files.copy(is, tempFile.toPath(), StandardCopyOption.REPLACE_EXISTING);
        }

        logger.info("Extracted Python script to: {}", tempFile.getAbsolutePath());
        return tempFile;
    }

    private void saveScrapedLinks(List<Map<String, String>> scrapedLinks) {
        for (Map<String, String> link : scrapedLinks) {
            String url = link.get("link");
            String title = link.get("title");

            if (url != null && title != null) {
                Optional<ModelInformer> existing = repository.findByUrl(url);

                if (existing.isEmpty()) {
                    ModelInformer newArticle = new ModelInformer(url, title);
                    repository.save(newArticle);
                    logger.info("Saved new article: {}", title);
                } else {
                    // Update title if needed
                    ModelInformer article = existing.get();
                    if (!article.getTitle().equals(title)) {
                        article.setTitle(title);
                        repository.save(article);
                        logger.info("Updated article title: {}", title);
                    }
                }
            }
        }
    }

    private List<ModelInformer> findUnvisitedWithKeywords() {
        // Create regex pattern for all keywords
        String pattern = KEYWORDS.stream()
                .map(Pattern::quote)
                .collect(Collectors.joining("|", "(?i)\\b(", ")\\b"));

        Criteria criteria = new Criteria().andOperator(
                Criteria.where("visited").is(false),
                Criteria.where("title").regex(pattern)
        );

        Query query = new Query(criteria);
        return mongoTemplate.find(query, ModelInformer.class);
    }

    public void markAsVisited(String id) {
        Optional<ModelInformer> article = repository.findById(id);
        if (article.isPresent()) {
            ModelInformer model = article.get();
            model.setVisited(true);
            repository.save(model);
            logger.info("Marked article as visited: {}", model.getTitle());
        }
    }

    public void markAsVisitedUsingLink(String link) {
        Optional<ModelInformer> article = repository.findByUrl(link);
        if (article.isPresent()) {
            ModelInformer model = article.get();
            model.setVisited(true);
            repository.save(model);
            logger.info("Marked article as visited: {}", model.getTitle());
        }
    }

    public void markMultipleAsVisited(List<String> ids) {
        for (String id : ids) {
            markAsVisited(id);
        }
    }
}