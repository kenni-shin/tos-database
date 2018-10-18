import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import {SkillBuilderComponent} from "./skill-builder/skill-builder.component";
import {SkillSimulatorRoutingModule} from "./skill-simulator-routing.module";
import {ClickOutsideModule} from "ng-click-outside";
import {FontAwesomeModule} from "@fortawesome/angular-fontawesome";
import {SharedModule} from "../shared/shared.module";
import {SkillBuilderJobComponent} from "./skill-builder/skill-builder-job/skill-builder-job.component";
import { SkillBuilderSkillComponent } from './skill-builder/skill-builder-skill/skill-builder-skill.component';
import {SkillBuilderJobSelectorComponent} from "./skill-builder/skill-builder-job-selector/skill-builder-job-selector.component";
import {SkillBuilderJobRankComponent} from "./skill-builder/skill-builder-job-rank/skill-builder-job-rank.component";
import {NgbModule} from "@ng-bootstrap/ng-bootstrap";
import {SkillBuilderJobRankListComponent} from "./skill-builder/skill-builder-job-rank-list/skill-builder-job-rank-list.component";
import { SkillBuilderStatSelectorComponent } from './skill-builder/skill-builder-stat-selector/skill-builder-stat-selector.component';
import {FormsModule} from "@angular/forms";

@NgModule({
  imports: [
    CommonModule,
    ClickOutsideModule,
    FontAwesomeModule,
    FormsModule,
    NgbModule,
    SharedModule,
    SkillSimulatorRoutingModule,
  ],
  declarations: [
    SkillBuilderComponent,
    SkillBuilderJobComponent,
    SkillBuilderJobSelectorComponent,
    SkillBuilderJobRankComponent,
    SkillBuilderSkillComponent,
    SkillBuilderJobRankListComponent,
    SkillBuilderStatSelectorComponent
  ]
})
export class SkillSimulatorModule { }