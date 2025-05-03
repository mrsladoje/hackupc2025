package com.pumpaj.evropo.controller;

import com.pumpaj.evropo.model.Model021;
import com.pumpaj.evropo.service.Service021;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api")
@CrossOrigin(origins = "*") // Allow CORS for development
public class Controller021 {

    @Autowired
    private Service021 service;

    @GetMapping("/viableLinks021")
    public ResponseEntity<List<Model021>> getViableLinks() {
        List<Model021> viableLinks = service.getViableLinks();
        return ResponseEntity.ok(viableLinks);
    }

    @PostMapping("/markVisited/{id}")
    public ResponseEntity<String> markAsVisited(@PathVariable String id) {
        service.markAsVisited(id);
        return ResponseEntity.ok("Article marked as visited");
    }

    @PostMapping("/markMultipleVisited")
    public ResponseEntity<String> markMultipleAsVisited(@RequestBody List<String> ids) {
        service.markMultipleAsVisited(ids);
        return ResponseEntity.ok("Articles marked as visited");
    }
}