package com.pumpaj.evropo.controller;

import com.pumpaj.evropo.model.ModelInformer;
import com.pumpaj.evropo.service.ServiceInformer;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/informer/")
@CrossOrigin(origins = "*") // Allow CORS for development
public class ControllerInformer {

    @Autowired
    private ServiceInformer service;

    @GetMapping("/viableLinks")
    public ResponseEntity<List<ModelInformer>> getViableLinks() {
        List<ModelInformer> viableLinks = service.getViableLinks();
        return ResponseEntity.ok(viableLinks);
    }

    // Scheduled task to run every 3 hours
    @Scheduled(fixedRate = 3 * 60 * 60 * 1000) // 3 hours in milliseconds
    public void scheduledGetViableLinks() {
        service.getViableLinks();
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