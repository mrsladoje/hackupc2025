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

import java.io.*;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.util.*;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

@Service
public class ServiceInformer {

    @Autowired
    private RepositoryInformer repository;

    @Autowired
    private MongoTemplate mongoTemplate;

    @Autowired
    private AnalyserService analyserService;

    @Value("${python.script.path.informer:scripts/scraper_informer_najnovije.py}")
    private String scriptPath;

    @Value("${python.executable.path:python}")
    private String pythonPath;

    private static final List<String> KEYWORDS = Arrays.asList(
            "protest", "protesta", "proteste", "protestu", "protestima", "protesti", "protestni", "protestna", "protestno",
            "blokad", "blokade", "blokadu", "blokadom", "blokadama", "blokira", "blokiraj", "blokirano",
            "student", "studenti", "studenta", "studente", "studentu", "studentski", "studentska", "studentsko", "studiraju",
            "šetnja", "šetnje", "šetnju", "šetnjom", "šetnjama", "šetn", "šeta", "hod", "marš", "demonstrac",
            "javni", "čas", "cas", "javnog", "javnom", "časa", "casa", "javnoj", "časov", "casov",
            "skupština", "skup", "okupljanje", "okupio", "okupila", "okupili", "okupljaj", "protest", "demonstrant",
            "profesor", "profesoru", "profesori", "profesorski", "profesorsku", "profesorske", "profesora", "profesorom", "profesorka",
            "blokaderi", "blokaderski", "ustaše", "boljševici", "plenum", "plenumaši", "blokaderska", "blokadera", "plenumaša", "plenumašu", "blokaderu", "obojena", "revolucija", "obojenu", "revoluciju", "obojene", "revolucije"
    );

    public List<ModelInformer> getViableLinks() {
        List<Map<String, String>> scrapedLinks = runPythonScraper();
        saveScrapedLinks(scrapedLinks);
        List<ModelInformer> viableLinks = findUnvisitedWithKeywords();

        for (ModelInformer link : viableLinks) {
            analyserService.analyseAndProcess(link.getUrl(), "informer.rs");
        }

        return viableLinks;
    }

    private List<Map<String, String>> runPythonScraper() {
        List<Map<String, String>> articles = new ArrayList<>();
        ObjectMapper objectMapper = new ObjectMapper();

        try {
            File tempScript = extractScriptFromClasspath();
            List<String> command = Arrays.asList(pythonPath, tempScript.getAbsolutePath());

            ProcessBuilder pb = new ProcessBuilder(command);
            pb.redirectErrorStream(true);
            Process process = pb.start();

            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream(), "UTF-8"));
            String line;

            while ((line = reader.readLine()) != null) {
                if (line.startsWith("{")) {
                    try {
                        @SuppressWarnings("unchecked")
                        Map<String, String> article = objectMapper.readValue(line, Map.class);
                        if (article.containsKey("title") && article.containsKey("link")) {
                            articles.add(article);
                            markAsVisitedUsingLink(article.get("link"));
                        }
                    } catch (Exception e) {
                        // Ignore parsing errors
                    }
                }
            }

            process.waitFor();
            tempScript.delete();

        } catch (Exception e) {
            e.printStackTrace(); // Consider proper error handling
        }

        return articles;
    }

    private File extractScriptFromClasspath() throws IOException {
        ClassPathResource resource = new ClassPathResource(scriptPath);
        File tempFile = File.createTempFile("scraper", ".py");
        tempFile.deleteOnExit();

        try (InputStream is = resource.getInputStream()) {
            Files.copy(is, tempFile.toPath(), StandardCopyOption.REPLACE_EXISTING);
        }
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
                } else {
                    ModelInformer article = existing.get();
                    if (!article.getTitle().equals(title)) {
                        article.setTitle(title);
                        repository.save(article);
                    }
                }
            }
        }
    }

    private List<ModelInformer> findUnvisitedWithKeywords() {
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
        }
    }

    public void markAsVisitedUsingLink(String link) {
        Optional<ModelInformer> article = repository.findByUrl(link);
        if (article.isPresent()) {
            ModelInformer model = article.get();
            model.setVisited(true);
            repository.save(model);
        }
    }

    public void markMultipleAsVisited(List<String> ids) {
        for (String id : ids) {
            markAsVisited(id);
        }
    }
}